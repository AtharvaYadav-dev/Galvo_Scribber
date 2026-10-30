from configparser import ConfigParser

config = ConfigParser()
config.read('config/config.ini')

if not config.has_section('hatch_profile_1'):
    config.add_section('hatch_profile_1')
config.set('hatch_profile_1', 'enable', 'True')
config.set('hatch_profile_1', 'pen_no', '0')
config.set('hatch_profile_1', 'line_space', '0.05')
config.set('hatch_profile_1', 'angle', '45.0')
config.set('hatch_profile_1', 'count', '1.0')

if not config.has_section('hatch_profile_2'):
    config.add_section('hatch_profile_2')
config.set('hatch_profile_2', 'enable', 'False')
config.set('hatch_profile_2', 'pen_no', '0')
config.set('hatch_profile_2', 'line_space', '0.05')

if not config.has_section('hatch_profile_3'):
    config.add_section('hatch_profile_3')
config.set('hatch_profile_3', 'enable', 'False')
config.set('hatch_profile_3', 'pen_no', '0')
config.set('hatch_profile_3', 'line_space', '0.05')

with open('config/config.ini', 'w', encoding='utf-8') as f:
    config.write(f)

print("config/config.ini updated successfully!")

