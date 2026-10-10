# EzCad Features: Hinglish Explanation & Implementation Guide

Yahan aapke handwritten list ke 11 points ka detailed explanation aur unhe apne project (Python/Galvo) me kaise implement karna hai, uska guide diya gaya hai.

### 1) Marking on curvature surface
**Hinglish:**
Yeh feature gol ya curved surfaces par laser se mark karne ke liye hota hai. Normal laser flat surface par mark karta hai, lekin agar surface curved hai (jaise pipe ya bangle), toh surface aage-peeche hone se focus change hota rehta hai aur marking dhundhli ho jati hai. Is feature se software automatically focal length adjust kar leta hai taaki design crisp aaye.

**How to do it (Implementation):**
Iske liye aapke paas 3D Galvo scanner hona chahiye (jisme Z-axis ya dynamic focusing lens ho) ya fir object ko move karne ke liye alag se motorized Z-axis ho. Software (Python) me hume object ki 3D profile (jaise cylinder ka radius aur curve) input leni hogi. Jab marking ho rahi ho, toh (X, Y) coordinates ke hisaab se Z-axis ka offset mathematically calculate karke controller ko 3D vectors (X, Y, Z) bhejne honge.

---

### 2) Marking on Rotary
**Hinglish:**
Agar koi cylindrical object (jaise ring, bottle, ya pen) par 360-degree round marking karni hai, toh rotary attachment ka use hota hai. Object ko motor se thoda-thoda gol ghumaya jata hai aur laser uspar line-by-line ya part-by-part mark karta hai.

**How to do it:**
Aapke hardware setup me ek stepper ya servo motor add karni hogi jo object ko rotate karegi. Python code me aapko apni design (CAD vectors) ko chhote-chhote vertical slices (strips) me divide karna hoga. Logic aise kaam karega:
1. Laser pehla chhota slice mark karega.
2. Fir software motor ko ek specific angle ghumane ka command dega.
3. Fir laser agla slice mark karega.
Yahi process repeat hoga jab tak marking puri na ho jaye.

---

### 3) Depth (focus) changing marking (3mm-5mm Max)
**Hinglish:**
Iska matlab hai 3D marking ya deep engraving, jisme laser ki depth ya focus continuously change ho rahi ho. Jaise kisi metal par gehri khudaai (deep engraving) karni ho, toh har ek layer jalne ke baad focus ko thoda niche (lagbhag 3mm se 5mm tak) dhakelna padta hai taaki laser ki beam patli aur powerful bani rahe.

**How to do it:**
Isko implement karne ke liye software me engraving ko "Multi-layer" (loops me) process banana hoga. Ek variable (e.g., `z_drop_per_layer`) set karna hoga. Ek layer ki marking complete hone ke baad software automatically Z-axis motor ya 3D galvo head ko utne `mm` niche karega, aur fir next layer mark hogi.

---

### 4) Surface texturing (100 µm - 250 µm)
**Hinglish:**
Surface texturing ka matlab hai kisi material (metal/plastic) ki surface par ek khaas pattern ya khurdurapan (roughness) banana (jaise 100 se 250 microns tak deep). Yeh object par grip badhane, friction create karne, ya sirf aesthetic (sundar design) purpose ke liye use hota hai.

**How to do it:**
Aapko apne code me complex hatch patterns (jaise cross-hatch, spirals, wavy lines, dots) generate karne ka algorithm likhna hoga. Saath hi, laser ki speed, power, aur frequency ko is tarah set (calibrate) karna hoga ki wo surface ko deeply cut na kare, balki sirf micro-level par pighla (melt) karke texture banaye.

---

### 5) Hard Plastic marking
**Hinglish:**
Hard plastics par mark karne ke liye laser ke parameters ko bahut carefully set karna padta hai taaki plastic gande tarike se jale (melt/burn) nahi, balki uspar clear contrast wala mark (white/dark frosting) ubhar kar aaye.

**How to do it:**
Apne software me ek "Material Library" ya "Presets" data structure (JSON/SQLite) banayein. Jab user dropdown se 'Hard Plastic' select kare, toh software automatically low power (10-20%), high speed, aur proper frequency (pulse rate) parameters set kar de.

---

### 6) Serial Number Auto Increment
**Hinglish:**
Jab company me bahut saare products par alag-alag serial number mark karna ho (jaise SN-001, SN-002, SN-003...), toh operator ko baar-baar type na karna pade. Software khud har marking ke baad number aage badha deta hai.

**How to do it:**
Apne GUI me ek section banayein jisme "Auto Increment" ka option ho. User se `Start Number`, `End Number`, aur `Increment Step` (+1 ya +2) input lein. Python code me ek counter track karein. Har baar jab laser firing ka event end ho, `current_number` ko increase kar dein, aur next firing se pehle us naye string (text) ko dobara vectors/hatch me convert kar lein.

---

### 7) Font Selection
**Hinglish:**
User apne hisaab se text ka font (Arial, Times New Roman, Cursive, etc.) select kar sake. Laser software me normal text word processors (jaise MS Word) ki tarah nahi chhapta, laser ko font ki outlines aur path chahiye hote hain.

**How to do it:**
Python me `freetype-py` ya `PIL` (Pillow) library ya fir Qt ki GUI font library ka use karke TrueType Font (`.ttf`) files ko read kiya ja sakta hai. In libraries se aap text se vector paths (bezier curves, lines) extract kar sakte hain. Un outlines ko laser ke samajhne wale G-code ya galvo vectors me convert karna padega aur andar lines (hatching) fill karni padegi.

---

### 8) Barcode / QR code
**Hinglish:**
Text ya data ko Barcode (lines) ya QR code (2D matrix) me convert karke mark karna, taaki baad me kisi scanner ya mobile se easily scan kiya ja sake.

**How to do it:**
Python me `qrcode` aur `python-barcode` naam ki bahut acchi open-source libraries aati hain. User ka text in libraries me pass karein, ye ek 2D matrix (black and white blocks/dots) return karegi. Un black blocks ke coordinates ko chhote-chhote rectangles (ya dots) me badal kar laser controller ko bhejna hoga (with full hatch fill).

---

### 9) Pause
**Hinglish:**
Marking process ko beech me rokna. Agar operator ko lagta hai object thoda hil gaya hai ya emergency hai, toh wo marking ko pause karke check kar sake aur wahi se resume kar sake.

**How to do it:**
Agar aapka controller ek stream me line-by-line commands (serial port/USB) bhejta hai, toh Python me multi-threading ya `QThread` ka use karein. Ek "Pause flag" (boolean True/False) banayein. Loop me check karein, agar flag `True` ho toh `time.sleep()` me chala jaye aur laser beam OFF kar de. Resume karne par flag `False` hoga aur next vector line bhejna shuru kar dega.

---

### 10) Auto Placement detection -> Use Camera
**Hinglish:**
Camera (webcam ya industrial camera) ki madad se object ki exact position (X, Y) aur rotation angle pata karna. Isse agar operator ne object thoda tedha rakha ho, toh laser automatically apne design ko ghumakar bilkul sahi jagah par mark karta hai. Jig banane ka time bachta hai.

**How to do it:**
Iske liye Python ki `OpenCV` (`cv2`) library ka use hota hai.
1. Camera feed se image frame capture karein.
2. Edge detection (Canny) ya Template Matching (feature matching jaise SIFT/ORB) karke object ko identify karein.
3. Object ka center (X, Y displacement) aur angle of rotation calculate karein.
4. Ab jo bhi marking vectors the, un par math ka Affine Transformation matrix (Translation + Rotation) apply karein. Isse marking path software me hi object ke upar align ho jayega.

---

### 11) Basic CAD facility
**Hinglish:**
Software ke andar hi basic shapes (line, rectangle, circle), text, aur vectors ko draw, scale, rotate, aur delete/edit karne ki facility. (Bilkul waise hi jaise CorelDraw, AutoCAD, ya EzCad ke workspace me hota hai).

**How to do it:**
Yeh aapke project ka GUI (Graphical User Interface) core part hai. Agar aap PyQt/PySide use kar rahe hain, toh `QGraphicsScene` aur `QGraphicsView` ka use karein. 
- Inme aasan se canvas (drawing board) ban jata hai. 
- Mouse events (click, drag, release) ko pakad kar shapes banani hongi.
- Har shape (jaise circle) ko ek Object/Class ki tarah store karein jiske x, y, radius, aur color attributes hon.
- Ek bounding box (selection box) banakar aisi functionality deni hogi ki user mouse se usko resize ya rotate kar sake.

---
**Advice for Future:** 
Ye saare features kisi bhi professional laser software me bohot ahem (important) hote hain. Aap inhe ek-ek karke apne `main.py` me add kar sakte hain. **Auto-increment, Font Selection, aur Barcode** implement karne me relatively easy hain, inko aap pehle try kar sakte hain. Camera aur CAD facility thode complex modules hain jinko alag alag class files banakar develop karna padega.
