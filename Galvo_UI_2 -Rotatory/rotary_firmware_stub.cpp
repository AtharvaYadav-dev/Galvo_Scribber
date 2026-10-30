/**
 * ============================================================================
 * ROTARY MARK & SPLIT-MARK-2 FIRMWARE STATE MACHINE & PROTOCOL STUB
 * Target Microcontroller: STM32F411 / STM32F401 "Black Pill" or ESP32-S3
 * Language: C++14 / Embedded C++
 * ============================================================================
 * 
 * Hardware Architecture:
 * - Galvo Interface: Dual DAC (SPI) or XY2-100 digital synchronous bus
 * - Stepper Motor Interface: STEP, DIR, ENABLE driven by Hardware Timer (TIM2/3)
 * - Laser Modulation: DB25 Power bus (PB0-PB7), MO (PA2), Booster/Gate (PB9), PRR (PA8)
 * - Galvo Motion Status: Galvo Pin J2-33 / Digital Input (PA1) with EXTI interrupt
 * 
 * Key Functions:
 * 1. Serial binary packet parser with CRC16-CCITT integrity verification.
 * 2. Deterministic, non-blocking hardware state machine.
 * 3. Timer-driven trapezoidal stepper acceleration profile generator.
 * 4. Microsecond laser delay coordination (LaserOnDelay, LaserOffDelay, SettlingDelay).
 * 5. Return-to-origin zero-drift pulse register tracking.
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#if defined(ARDUINO)
  #include <Arduino.h>
#else
  // Native STM32 HAL / CMSIS fallback declarations for standalone compilation
  typedef void* HardwareTimer;
  #define HIGH 1
  #define LOW  0
  void digitalWrite(uint8_t pin, uint8_t val) {}
  uint8_t digitalRead(uint8_t pin) { return 0; }
  void delayMicroseconds(uint32_t us) {}
  uint32_t micros(void) { return 0; }
  uint32_t millis(void) { return 0; }
#endif

// ============================================================================
// 1. HARDWARE PIN DEFINITIONS (STM32 Black Pill & Galvo DB25 Integration)
// ============================================================================
namespace PinMap {
    // Stepper Motor: Rotary Chuck Motor routed via Z-Axis Driver (Hardware Axis 2)
    // When Rotary mode is active, Z-axis STEP/DIR signals advance the rotary chuck.
    constexpr uint8_t ROT_STEP_PIN    = 15; // Z-STEP (TIM3_CH1 / PB12)
    constexpr uint8_t ROT_DIR_PIN     = 16; // Z-DIR (PB13)
    constexpr uint8_t ROT_ENABLE_PIN  = 17; // Z-ENABLE (PB14, Active LOW)

    // Galvo Scan Hardware Feedback
    constexpr uint8_t GALVO_BUSY_IN   = 1;  // PA1 (HIGH while mirrors are slewing)
    constexpr uint8_t RED_DOT_PIN     = 4;  // PA4 (Red aiming diode)

    // Laser Control Interlocks
    constexpr uint8_t LASER_MO_PIN    = 2;  // PA2 (Master Oscillator)
    constexpr uint8_t LASER_GATE_PIN  = 9;  // PB9 (High-Speed Emission Booster Gate)
    constexpr uint8_t LASER_LATCH_PIN = 8;  // PB8 (DB25 8-bit power latch)
}

// ============================================================================
// 2. BINARY PACKET PROTOCOL DEFINITION (HOST <-> MCU)
// ============================================================================
#pragma pack(push, 1)

constexpr uint8_t PKT_MAGIC_0 = 0xAA;
constexpr uint8_t PKT_MAGIC_1 = 0x55;

enum Opcode : uint8_t {
    CMD_PING                 = 0x10,
    CMD_ROTARY_CONFIG        = 0x20,
    CMD_ROTARY_JOG           = 0x21,
    CMD_ROTARY_ZERO          = 0x22,
    CMD_ROTARY_TEST_360      = 0x23,
    CMD_SPLIT_MARK_BEGIN     = 0x30,
    CMD_SPLIT_SLICE_LOAD     = 0x31,
    CMD_SPLIT_SLICE_START    = 0x32,
    CMD_EMERGENCY_STOP       = 0x33,
    CMD_GET_STATUS           = 0x40,

    RESP_ACK                 = 0x80,
    RESP_STATUS              = 0x81,
    EVENT_SLICE_COMPLETED    = 0x82,
    EVENT_JOB_FINISHED       = 0x83,
    RESP_ERROR               = 0x8F
};

struct PacketHeader {
    uint8_t magic0;      // 0xAA
    uint8_t magic1;      // 0x55
    uint8_t seq;         // Sequence counter
    uint8_t opcode;      // Opcode
    uint16_t length;     // Payload byte length
};

struct ConfigPayload {
    uint32_t pulses_per_rev;   // P_rev (e.g. 6400)
    float    gear_ratio;       // Gear ratio (e.g. 1.0f)
    float    diameter_mm;      // Part diameter (e.g. 25.0f)
    uint32_t max_speed_pps;    // Max stepper speed in pulses/sec
    uint16_t accel_time_ms;    // Acceleration ramp duration
    uint16_t settling_delay_ms;// Delay to damp chuck vibration
    uint8_t  reverse_dir;      // 0 = Normal, 1 = Reversed
    uint8_t  return_to_zero;   // 1 = Rotate back to start upon job completion
};

struct JogPayload {
    int32_t  pulses;           // Relative pulse move
    uint32_t speed_pps;        // Velocity
};

struct SliceLoadPayload {
    uint16_t slice_index;      // 0-indexed slice
    uint16_t total_slices;     // Total slices in job
    int32_t  step_pulses;      // Relative stepper pulses to advance before marking
    uint16_t vector_count;     // Number of 2D galvo points following
};

struct StatusResponsePayload {
    uint8_t  state;            // Current RotaryMarkState
    uint16_t current_slice;    // Currently executing slice
    int32_t  stepper_position; // Absolute pulse counter since origin
    uint8_t  laser_active;     // Laser emission flag
    uint8_t  error_code;       // Fault code
};

#pragma pack(pop)

// CRC16-CCITT (Polynomial 0x1021, Initial 0xFFFF)
uint16_t compute_crc16(const uint8_t* data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t b = 0; b < 8; b++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

// ============================================================================
// 3. FIRMWARE STATE MACHINE DEFINITION
// ============================================================================
enum class RotaryMarkState : uint8_t {
    IDLE = 0,
    SLICE_LOADED,
    STEPPER_ACCEL,
    STEPPER_RUN,
    STEPPER_DECEL,
    SETTLING_DELAY,
    GALVO_SCANNING,
    LASER_OFF_DELAY,
    SLICE_COMPLETE,
    RETURN_TO_ZERO,
    ESTOP_HALTED
};

class RotaryMarkingController {
public:
    RotaryMarkingController()
        : state_(RotaryMarkState::IDLE),
          current_slice_(0),
          total_slices_(0),
          stepper_pos_(0),
          job_initial_pos_(0),
          stepper_target_pulses_(0),
          stepper_remaining_pulses_(0),
          stepper_current_speed_(0.0f),
          settle_timer_start_us_(0),
          laser_off_timer_start_us_(0),
          is_redlight_only_(false) {
        
        // Default Industrial Settings (EZCad Compatible)
        config_.pulses_per_rev = 6400;
        config_.gear_ratio = 1.0f;
        config_.diameter_mm = 25.0f;
        config_.max_speed_pps = 3000;
        config_.accel_time_ms = 80;
        config_.settling_delay_ms = 120;
        config_.reverse_dir = 0;
        config_.return_to_zero = 1;
    }

    void init() {
        // Configure GPIO states
        digitalWrite(PinMap::ROT_ENABLE_PIN, LOW); // Active
        digitalWrite(PinMap::ROT_STEP_PIN, LOW);
        digitalWrite(PinMap::ROT_DIR_PIN, LOW);

        digitalWrite(PinMap::LASER_GATE_PIN, LOW); // Safe - Optical beam clamped OFF
        digitalWrite(PinMap::LASER_MO_PIN, LOW);
        digitalWrite(PinMap::RED_DOT_PIN, LOW);

        state_ = RotaryMarkState::IDLE;
    }

    // --- High-Frequency Periodic Task (Invoked in Main Loop) ---
    void update() {
        switch (state_) {
            case RotaryMarkState::IDLE:
                break;

            case RotaryMarkState::SLICE_LOADED:
                // If stepper must advance to reach slice position, initiate movement
                if (stepper_target_pulses_ != 0) {
                    start_stepper_move(stepper_target_pulses_);
                } else {
                    // No stepper move needed; start galvo scan immediately
                    start_galvo_scan();
                }
                break;

            case RotaryMarkState::STEPPER_ACCEL:
            case RotaryMarkState::STEPPER_RUN:
            case RotaryMarkState::STEPPER_DECEL:
                // Stepper pulse generation is driven by Timer ISR.
                // We check if the ISR has completed the commanded step quota:
                if (stepper_remaining_pulses_ == 0) {
                    settle_timer_start_us_ = micros();
                    state_ = RotaryMarkState::SETTLING_DELAY;
                }
                break;

            case RotaryMarkState::SETTLING_DELAY: {
                // Wait settling duration to eliminate mechanical chuck vibration
                uint32_t elapsed_ms = (micros() - settle_timer_start_us_) / 1000;
                if (elapsed_ms >= config_.settling_delay_ms) {
                    if (is_returning_to_zero_) {
                        is_returning_to_zero_ = false;
                        state_ = RotaryMarkState::IDLE;
                        send_event(EVENT_JOB_FINISHED, nullptr, 0);
                    } else {
                        start_galvo_scan();
                    }
                }
                break;
            }

            case RotaryMarkState::GALVO_SCANNING:
                // Monitored via Galvo Busy Pin or Galvo Complete Interrupt
                // In hardware: Galvo Card brings GALVO_BUSY_IN LOW upon queue completion
                if (digitalRead(PinMap::GALVO_BUSY_IN) == LOW) {
                    // Scan finished -> clamp laser gate OFF immediately
                    digitalWrite(PinMap::LASER_GATE_PIN, LOW);
                    laser_off_timer_start_us_ = micros();
                    state_ = RotaryMarkState::LASER_OFF_DELAY;
                }
                break;

            case RotaryMarkState::LASER_OFF_DELAY: {
                // Microsecond settling after laser shutoff
                constexpr uint32_t LASER_OFF_DELAY_US = 150; // 150 us
                if (micros() - laser_off_timer_start_us_ >= LASER_OFF_DELAY_US) {
                    state_ = RotaryMarkState::SLICE_COMPLETE;
                    on_slice_complete();
                }
                break;
            }

            case RotaryMarkState::SLICE_COMPLETE:
                // Host will acknowledge or send next slice
                break;

            case RotaryMarkState::RETURN_TO_ZERO: {
                int32_t delta_to_origin = job_initial_pos_ - stepper_pos_;
                if (delta_to_origin != 0) {
                    is_returning_to_zero_ = true;
                    start_stepper_move(delta_to_origin);
                } else {
                    state_ = RotaryMarkState::IDLE;
                    send_event(EVENT_JOB_FINISHED, nullptr, 0);
                }
                break;
            }

            case RotaryMarkState::ESTOP_HALTED:
                emergency_shutdown();
                break;
        }
    }

    // --- Command Handlers ---
    void handle_config(const ConfigPayload& payload) {
        config_ = payload;
        send_ack(CMD_ROTARY_CONFIG);
    }

    void handle_jog(const JogPayload& payload) {
        if (state_ != RotaryMarkState::IDLE) {
            send_error(0x01, "Busy; cannot jog.");
            return;
        }
        start_stepper_move(payload.pulses);
        send_ack(CMD_ROTARY_JOG);
    }

    void handle_zero() {
        stepper_pos_ = 0;
        send_ack(CMD_ROTARY_ZERO);
    }

    void handle_test_360() {
        if (state_ != RotaryMarkState::IDLE) {
            send_error(0x01, "Busy; cannot test revolution.");
            return;
        }
        int32_t rev_pulses = (int32_t)(config_.pulses_per_rev * config_.gear_ratio);
        if (config_.reverse_dir) rev_pulses = -rev_pulses;
        start_stepper_move(rev_pulses);
        send_ack(CMD_ROTARY_TEST_360);
    }

    void handle_slice_load(const SliceLoadPayload& payload, const uint8_t* vector_data) {
        current_slice_ = payload.slice_index;
        total_slices_ = payload.total_slices;
        stepper_target_pulses_ = payload.step_pulses;

        if (current_slice_ == 0) {
            job_initial_pos_ = stepper_pos_; // Record origin for return-to-zero
        }

        // Buffer galvo vectors into local DMA memory...
        state_ = RotaryMarkState::SLICE_LOADED;
        send_ack(CMD_SPLIT_SLICE_LOAD);
    }

    void handle_estop() {
        state_ = RotaryMarkState::ESTOP_HALTED;
        emergency_shutdown();
        send_ack(CMD_EMERGENCY_STOP);
    }

    // --- Hardware Interrupts ---
    void timer_stepper_isr() {
        // Executed at up to 50 kHz from TIM2/TIM3 Interrupt
        if (stepper_remaining_pulses_ > 0) {
            // Pulse STEP pin
            digitalWrite(PinMap::ROT_STEP_PIN, HIGH);
            delayMicroseconds(2);
            digitalWrite(PinMap::ROT_STEP_PIN, LOW);

            stepper_pos_ += stepper_dir_sign_;
            stepper_remaining_pulses_--;

            // Simple trapezoidal ramp adjustment
            // (Adjust TIM->ARR reload register here for acceleration)
        }
    }

    void galvo_scan_complete_isr() {
        // Interrupt from Galvo Scanner Controller Pin when vector list completes
        if (state_ == RotaryMarkState::GALVO_SCANNING) {
            digitalWrite(PinMap::LASER_GATE_PIN, LOW); // Immediate cut
            laser_off_timer_start_us_ = micros();
            state_ = RotaryMarkState::LASER_OFF_DELAY;
        }
    }

private:
    void start_stepper_move(int32_t pulses) {
        if (pulses == 0) return;

        bool dir_forward = (pulses > 0);
        if (config_.reverse_dir) dir_forward = !dir_forward;

        digitalWrite(PinMap::ROT_DIR_PIN, dir_forward ? HIGH : LOW);
        stepper_dir_sign_ = (pulses > 0) ? +1 : -1;
        stepper_remaining_pulses_ = (uint32_t)abs(pulses);

        state_ = RotaryMarkState::STEPPER_ACCEL;
    }

    void start_galvo_scan() {
        state_ = RotaryMarkState::GALVO_SCANNING;

        // Un-clamp laser interlock and trigger hardware vector queue execution
        if (!is_redlight_only_) {
            digitalWrite(PinMap::LASER_MO_PIN, HIGH);
            digitalWrite(PinMap::LASER_GATE_PIN, HIGH);
        } else {
            digitalWrite(PinMap::RED_DOT_PIN, HIGH);
        }

        // Trigger GT5 / XY2-100 scan start
    }

    void on_slice_complete() {
        // Notify host that slice is complete
        uint16_t completed_idx = current_slice_;
        send_event(EVENT_SLICE_COMPLETED, (const uint8_t*)&completed_idx, sizeof(completed_idx));

        if (current_slice_ + 1 >= total_slices_) {
            if (config_.return_to_zero) {
                state_ = RotaryMarkState::RETURN_TO_ZERO;
            } else {
                state_ = RotaryMarkState::IDLE;
                send_event(EVENT_JOB_FINISHED, nullptr, 0);
            }
        }
    }

    void emergency_shutdown() {
        // Cut all laser emission immediately
        digitalWrite(PinMap::LASER_GATE_PIN, LOW);
        digitalWrite(PinMap::LASER_MO_PIN, LOW);
        digitalWrite(PinMap::RED_DOT_PIN, LOW);

        // Stop stepper pulse generation
        stepper_remaining_pulses_ = 0;
        stepper_target_pulses_ = 0;
    }

    void send_ack(uint8_t op) {
        // Send ACK packet back to Host PC over Serial USB/UART
    }

    void send_error(uint8_t code, const char* msg) {
        // Send Error packet
    }

    void send_event(uint8_t event_code, const uint8_t* data, uint16_t len) {
        // Stream asynchronous event notification
    }

    // State Variables
    RotaryMarkState state_;
    ConfigPayload config_;
    uint16_t current_slice_;
    uint16_t total_slices_;
    int32_t stepper_pos_;
    int32_t job_initial_pos_;
    int32_t stepper_target_pulses_;
    volatile uint32_t stepper_remaining_pulses_;
    int8_t  stepper_dir_sign_;
    float   stepper_current_speed_;

    uint32_t settle_timer_start_us_;
    uint32_t laser_off_timer_start_us_;
    bool is_redlight_only_;
    bool is_returning_to_zero_ = false;
};

// Global Controller Instance
static RotaryMarkingController g_rotary_controller;

// Entry points for MCU firmware integration
void rotary_firmware_setup() {
    g_rotary_controller.init();
}

void rotary_firmware_loop() {
    g_rotary_controller.update();
}
