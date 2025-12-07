#mport rpi_ws281x
import board
import neopixel
from time import sleep
import datetime
import random
import argparse
import regex


# light_red = (0, 128, 0)
red = (0, 255, 0)
orange = (90, 255, 0)
yellow = (255, 255, 0)
lime_green = (255, 128, 0)
green = (255, 0, 0)
weird_green = (255, 0, 50)
teal = (255, 0, 255)
alt_blue = (128, 0, 255)
blue = (0, 0, 255)
purple = (0, 127, 255)
dark_purple = (0, 128, 128)
pink = (0, 255, 255)
fuschia = (0, 255, 127)
white = (255, 255, 255)

color_list = [red, orange, yellow, lime_green, green, weird_green, teal, alt_blue, blue, purple, dark_purple, pink, fuschia, white]
color_list_no_white = [red, orange, yellow, lime_green, green, weird_green, teal, alt_blue, blue, purple, dark_purple, pink, fuschia]
color_dict = {"red": red,
              "orange": orange,
              "yellow": yellow,
              "lime_green": lime_green,
              "green": green,
              "weird_green": weird_green,
              "teal": teal,
              "alt_blue": alt_blue,
              "blue": blue,
              "purple": purple,
              "dark_purple": dark_purple,
              "pink": pink,
              "fuschia": fuschia,
              "white": white}

def set_single_color(pixels, color, brightness=1):
    pixels.brightness = brightness
    pixels.fill(color_dict[color])


def set_color_from_grb(pixels, g, r, b, brightness=1):
    pixels.brightness = brightness
    pixels.fill((g, r, b))


def list_available_colors():
    printable_color_list = [x for x in color_dict.keys()]
    print(printable_color_list)


def get_random_color(pixels):
    color_one = random.randint(0, 255)
    color_two = random.randint(0, 255)
    color_three = random.randint(0, 255)

    return (color_one, color_two, color_three)

# pixels[0] = purple
# pixels.show()
# sleep(5)

def loop_random_colors(pixels):
    while True:
        for led_number in range(50):
            pixels[led_number] = random.choice(color_list)
            sleep(0.02)

def all_colors(pixels, num_lights):
    lights_per_color = num_lights / len(color_list)
    current_light_count = lights_per_color
    color_position = 0
    # print(f"lights per color: {lights_per_color}")

    for num in range(num_lights):
        if num < current_light_count:
            pixels[num] = color_list[color_position]
        else:
            current_light_count += lights_per_color
            color_position += 1
            pixels[num] = color_list[color_position]

def custom_wave(pixels, user_color_list, color_delay):
    # write a new wave function where a list of pixels is initialized and a list of lists ([[color, num_remaining], [etc.]])
    # is used for putting new colors at the beginning of the pixels
    # this should allow for making the thing infinite, should allow for randomness or christmasness
    # and will hopefully be faster
    # user_color_list = [["purple", 4], ["green", 4]]
    temp_list = [white] * len(pixels)

    while True:
        for each_color in user_color_list:
            if each_color[0] == "random":
                this_color = random.choice(color_list)
            else:
                this_color = color_dict[each_color[0]]
            num_bulbs = each_color[1]

            while num_bulbs > 0:
                # print('in here')
                temp_list = [this_color] + temp_list[:-1]
                pixels[::] = temp_list
                num_bulbs -= 1
                sleep(color_delay)
            # print("broke out?")


def white_rainbow_wave(pixels, num_lights, sleep_time, wave_length):
    # CONTINUE HERE: I have a few different wave ideas:
    # allow setting the speed of this wave
    # allow for setting a number waves to be chasing each other
    # setting only specific colors in the wave?
    pixels.fill(white)
    color_position = 0
    accessible_num = 0
    for num in range(num_lights):
        accessible_num = num
        # print("")
        # if num % 2 == 0:
        #     # color_position += 1
        #
        #     if color_position >= len(color_list_no_white):
        #         color_position = 0
        #
        pixels[num] = color_list_no_white[color_position]

        temp_color_position = color_position
        for reversed_counter, reversed_num in enumerate(reversed(range(num))):
            # print(f"in reverse loop - num: {num}, reversed_num: {reversed_num}, reversed_counter: {reversed_counter}, reversed_counter % wave_length: {reversed_counter % wave_length}")
            if reversed_counter % wave_length == wave_length - 1:
            # if (wave_length - 1) % wave_length == 1:
                # print("temp_color_position is updating")
                temp_color_position += 1
            if temp_color_position >= len(color_list_no_white):
                pixels[reversed_num] = white
                break
            pixels[reversed_num] = color_list_no_white[temp_color_position]


        sleep(sleep_time)

    colors_complete = False
    while not colors_complete:
        accessible_num += 1
        temp_color_position = 0
        color_changed = False
        for reversed_counter, reversed_num in enumerate(reversed(range(accessible_num))):
            if reversed_counter % wave_length == wave_length - 1:
                temp_color_position += 1
            if reversed_num < num_lights:
                color_changed = True
                if temp_color_position >= len(color_list_no_white):
                    pixels[reversed_num] = white
                    if reversed_num + 1 >= num_lights:
                        colors_complete = True
                    break
                pixels[reversed_num] = color_list_no_white[temp_color_position]

        if color_changed:
            sleep(sleep_time)


def flash(pixels, color, sleep_time):
    while True:
        pixels.fill(color)
        sleep(sleep_time)
        pixels.fill((0, 0, 0))
        sleep(sleep_time)


def pulse(pixels, color, time, special_mode=None):
    num_brightness_changes = 200
    individual_step = 1 / (num_brightness_changes / 2)
    current_brightness = 0
    time_between_changes = time / num_brightness_changes
    set_single_color(pixels, color, brightness=current_brightness)
    if special_mode == "christmas":
        temp_list_green = [green] * len(pixels) 
        temp_list_red = [red] * len(pixels)
        temp_list_white = [white] * len(pixels)
        pixels[::3] = temp_list_green
        pixels[1::3] = temp_list_red
        pixels[2::3] = temp_list_white

    current_direction = "decreasing"
    while True:
        if current_direction == "increasing":
            current_brightness += individual_step
            if current_brightness >= 1:
                current_brightness = 1
                current_direction = "decreasing"
        if current_direction == "decreasing":
            current_brightness -= individual_step
            if current_brightness <= 0:
                current_brightness = 0
                if special_mode:
                    if special_mode == "random":
                        new_color = color_dict[random.choice([x for x in color_dict.keys()])]
                        pixels.fill(new_color)
                    if special_mode == "christmas":
                        first_element = pixels[0]
                        temp_list = pixels[1:]
                        temp_list.append(first_element)
                        pixels[::] = temp_list
                current_direction = "increasing"

        pixels.brightness = current_brightness
        sleep(time_between_changes)


def call_chaos(pixels, user_color_list):
    start_time = datetime.datetime.now()
    total_time_elapsed = 0
    temp_list = [white] * len(pixels)

    index_list = []
    for num in range(len(pixels)):
        index_list.append(num)

    while True:
        random_time = random.randrange(1, 10, 1) / 100
        total_time_elapsed += random_time

        num_leds_to_change = random.choice(index_list)
        random_indices = random.choices(index_list, k=num_leds_to_change)

        for each_pixel in random_indices:
            this_color = random.choice(user_color_list)
            if this_color == "random":
                temp_list[each_pixel] = random.choice(color_list)
            else:
                temp_list[each_pixel] = color_dict[this_color]

        pixels[::] = temp_list
        random_indices = random.choices(index_list, k=5)
        sleep(random_time)

        # print(f"random time added: {total_time_elapsed}")
        # print(f"actual time passed: {datetime.datetime.now() - start_time}\n")

def wave(pixels, background_color, user_color_list, wave_gap_distance, wave_length):
    print(f"doin' the wave - these are the colors: {user_color_list}, background: {background_color}, gap: {wave_gap_distance}, length: {wave_length}")

    temp_time = 0.5
    num_lights = len(pixels)

    temp_list = [color_dict[background_color]] * num_lights
    wave_color_number = 0
    current_color_pixel_number = 0
    if user_color_list[0] == "random":
        first_color = random.choice(color_list)
    else:
        first_color = color_dict[user_color_list[0]]
    color_position_stack = [[first_color, 0]]
    temp_list[0] = color_position_stack[0][0]
    while True:
        for each_wave in color_position_stack:
            next_lead = each_wave[1] += 1

        sleep(temp_time)


def turn_off(pixels):
    pixels.deinit()


def set_pixels(num_lights=50):
    pixels = neopixel.NeoPixel(board.D18, num_lights, brightness=1.00, auto_write=True)
    return pixels


def main():
    num_lights = 50
    # pixels = neopixel.NeoPixel(board.D18, num_lights, brightness = 1.00, auto_write=True)
    pixels = set_pixels()
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--testing", action="store_true")
    parser.add_argument("-c", "--single_color", type=str, help="Set a single color")
    parser.add_argument("-r", "--random_colors", help="Set lights to rotate random colors", action="store_true")
    parser.add_argument("-a", "--all_colors", help="Set all 'available' colors", action="store_true")
    parser.add_argument("-v", "--grb_value", help="Set an rgb (grb) value in the format '(g, r, b)'", type=str)
    parser.add_argument("-rm", "--rainbow_march", help="Do a rainbow march - arguments are sleep time and wave length, e.g., '0.25 5'", type=str)
    parser.add_argument("-f", "--flash", help="Color and sleep time for flashing a single color in the format 'color time', e.g., 'blue 0.1'", type=str)
    parser.add_argument("-p", "--pulse", help="Pulse color in and out at a selected speed in the format 'color time' where time is total amount of time between peaks.")
    parser.add_argument("-l", "--list_colors", help="List all named colors", action="store_true")
    # parser.add_argument("-cp", "--christmas_pulse", help="Pulse red, green, and white with a specified time between brightness peaks, e.g., '0.75'")
    parser.add_argument("-cw", "--custom_wave", help="Custom wave - enter colors, the number of bulbs to be lit for each color, and the sleep time, e.g., '(green 3) (red 3) 0.75'")
    parser.add_argument("-ch", "--chaos", help="Chaos: select colors to choose from (or simply enter 'random') in the format 'red, blue, purple, orange' or 'random'")
    parser.add_argument("-w", "--wave", help="Wave: waves against a background of your choosing with a specified distance between waves and wave length in the format '(background)(color1 color2)5 4'")
    parser.add_argument("-x", "--off", help="Turn all lights off", action="store_true")

    args = parser.parse_args()
    # print(f"args? {args}")

    if args.testing:
        # new_rainbow(pixels)
        combined_list = [0] * num_lights
        combined_list[::2] = [red] * (len(pixels) // 2)
        combined_list[1::2] = [blue] * (len(pixels) // 2)
        pixels[::] = combined_list

    elif args.single_color:
        color = args.single_color

        if color in color_dict:
            print(f"setting {color_dict[color]}")
            set_single_color(pixels, color)
        else:
            print(f"{color} is not a valid color, please try again (I'll get a list of available colors eventually)")

    elif args.random_colors:
        loop_random_colors(pixels)

    elif args.all_colors:
        all_colors(pixels, num_lights)

    elif args.grb_value:
        rgb_regex = regex.search(r"\(((?:\d|\d\d|[0-1]\d\d|2\d[0-5])), ((?:\d|\d\d|[0-1]\d\d|2\d[0-5])), ((?:\d|\d\d|[0-1]\d\d|2\d[0-5]))\)", args.grb_value)
        if rgb_regex:
            green_value = int(rgb_regex.group(1))
            red_value = int(rgb_regex.group(2))
            blue_value = int(rgb_regex.group(3))
            # print(f"???? {green_value}, {}, {}")
            set_color_from_grb(pixels, green_value, red_value, blue_value)
        else:
            print("not a valid color value, please try again")

    elif args.rainbow_march:
        float_match = regex.search(r"^(\d+|\d+\.\d+|\.\d+) (\d+)$", args.rainbow_march)
        if float_match:
            sleep_time = float(float_match.group(1))
            wave_length = int(float_match.group(2))
            white_rainbow_wave(pixels, num_lights, sleep_time, wave_length)
        else:
            print("not a valid sleep time, please try again")

    elif args.flash:
        flash_match = regex.search(r"^(\w+) (\d+|\d+\.\d+|\.\d+)$", args.flash)
        if flash_match:
            color = flash_match.group(1)
            sleep_time = float(flash_match.group(2))
            if color in color_dict:
                flash(pixels, color_dict[color], sleep_time)
            else:
                print("that color is invalid, please try again")
        else:
            print("that input is invalid, please try again")

    elif args.pulse:
        pulse_match = regex.search(r"^(\w+) +(\d+|\d+\.\d+|\.\d+)$", args.pulse)
        special_mode = ""
        if not pulse_match:
            print("not a valid input, plese try again")
        else:
            color = pulse_match.group(1).lower()
            time = float(pulse_match.group(2))
            if color == "random":
                special_mode = "random"
                color = random.choice([x for x in color_dict.keys()])
            elif color == "christmas":
                print("doin' christmas stuff")
                special_mode = "christmas"
                color = "white"
            elif color not in color_dict:
                print("that's not a good color")

        pulse(pixels, color, time, special_mode)

    elif args.custom_wave:
        custom_wave_match = regex.search(r"^((?:\([^\n\)\(]+\) *)+) +(\d|\d*\.\d+)$", args.custom_wave)
        if custom_wave_match:
            color_list = custom_wave_match.group(1)
            delay_time = float(custom_wave_match.group(2))
            color_split = regex.split(r"\(|\)", color_list)
            color_repeat_regex = regex.compile(r"^(\w+) *(\d+)$")
            valid_colors = []
            input_is_valid = True
            for each_color in color_split:
                if each_color.strip():
                    color_match = color_repeat_regex.match(each_color)
                    if not color_match:
                        print(f"the format of this color is not valid: {each_color}")
                        input_is_valid = False
                    else:
                        this_color = color_match.group(1).lower()
                        num_lights = int(color_match.group(2))
                        if this_color == "random":
                            valid_colors.append(["random", num_lights])
                        elif this_color not in color_dict:
                            print(f"{this_color} is not a vlaid color")
                            input_is_valid = False
                        else:
                            valid_colors.append([this_color, num_lights])
            if input_is_valid:
                # print(f"this is just a list of colors, right? {valid_colors}")
                custom_wave(pixels, valid_colors, delay_time)
        else:
            print(f"not a valid input, please try again - format: '(blue 2) (green 2) (red 2) 0.75'")

    elif args.chaos:
        print("this is chaos!")
        chaos_match = regex.split(r", *", args.chaos)
        user_color_list = []
        input_is_valid = True
        for each_color in chaos_match:
            this_color = each_color.strip().lower()
            if this_color:
                if this_color == "random":
                    user_color_list.append("random")
                elif this_color not in color_dict:
                    print(f"{this_color} is not a valid color")
                    input_is_valid = False
                else:
                    user_color_list.append(this_color)

        if input_is_valid:
            call_chaos(pixels, user_color_list)

    elif args.wave:
        wave_match = regex.search(r"^\(([^\(\)]+)\) *\(([^\n\(\)]+)\) *([0-9]+) *([0-9]+)$", args.wave)
        if not wave_match:
            print("the format of the argument is not correct - please try again")
        else:
            background_color = wave_match.group(1).lower().strip()
            wave_color_match = wave_match.group(2).lower().strip()
            wave_gap_distance = int(wave_match.group(3))
            wave_length = int(wave_match.group(4))

            color_split = regex.split(r" +", wave_color_match)
            user_color_list = []

            colors_match = True
            if background_color not in color_dict and background_color != "random":
                print(f"{background_color} is not a valid color")
                colors_match = False

            for each_color in color_split:
                if each_color not in color_dict and each_color != "random":
                    print(f"{each_color} is not a valid color")
                    colors_match = False
                else:
                    user_color_list.append(each_color)

            if colors_match:
                wave(pixels, background_color, user_color_list, wave_gap_distance, wave_length)

    elif args.list_colors:
        list_available_colors()

    elif args.off:
        turn_off(pixels)

    else:
        print("wtf")

if __name__ == "__main__":
    main()
