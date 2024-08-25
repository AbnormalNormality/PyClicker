from tkinter import Tk, Label, Frame, simpledialog, messagebox, StringVar, Toplevel
from PIL import ImageTk, Image
from base64 import b64encode, b64decode
from json import dumps, loads
from os.path import exists
from binascii import Error
from random import choice
from math import ceil, floor
from tkinter.ttk import Button, Radiobutton, OptionMenu
from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO
from google.auth.exceptions import TransportError
from threading import Thread
from uuid import uuid4
from webbrowser import open as w_open
from firebase_admin.exceptions import UnavailableError
from sys import argv

from google.oauth2 import service_account

from AliasTkFunctions import fix_resolution_issue, resize_window, create_scrollable_frame, update_bg, create_tooltip
from AliasGeneralFunctions import shorten_number, time_to_units, manage_variable

from dev_tools import *

fix_resolution_issue()

main = Tk()
resize_window(main, 3, 3, False)

player = {}


# noinspection PyUnresolvedReferences,PyTypeChecker
def load(new_game=False):
    global player
    # noinspection SpellCheckingInspection
    player = {
        # flags
        "cheater": False,
        "autosave": True,

        "version": ("0.4.3", "- Alpha"),

        "user_id": str(uuid4()),
        "online": {
            "hs_holder": False,
            "lr_holder": False,
            "ma_holder": False
        },

        "redeemed_codes": [],

        "event_bonus": True,

        "mods": {
            "neverclick": False,
            "onstrike": False,
            "primitive": False
        },

        # values
        "money": 0,
        "total_money": 0,
        "highscore": 0,

        "cpc": 1,
        "cooldown": 75,
        "cpc_bonus": 0.01,

        "cps_speed": 1,

        # time related
        "run_start": datetime.now(),
        "last_on": datetime.now(),
        "last_check": datetime.now(),

        # buildings and upgrades
        "buildings": {
            "1": {
                "cost": 10,
                "owned": 0,
                "cps": 0.1,
                "tooltip": "Makes $1 every 10 seconds.\n\n\"Look ma, it's me!\"",
                "name": "Alia"
            },

            "2": {
                "cost": 100,
                "owned": 0,
                "cps": 1,
                "name": "2"
            },

            "3": {
                "cost": 1000,
                "owned": 0,
                "cps": 10,
                "name": "3"
            },

            "4": {
                "cost": 10000,
                "owned": 0,
                "cps": 100,
                "name": "4"
            },

            "5": {
                "cost": 100000,
                "owned": 0,
                "cps": 1000,
                "name": "5"
            },

            "6": {
                "cost": 1000000,
                "owned": 0,
                "cps": 10000,
                "name": "6"
            },

            "7": {
                "cost": 10000000,
                "owned": 0,
                "cps": 100000,
                "name": "7"
            },

            "8": {
                "cost": 100000000,
                "owned": 0,
                "cps": 1000000,
                "name": "8"
            }
        },

        "upgrades": {
            "1": {
                "targets": "buildings",
                "unlocked": False,
                "args": ("normal", 1.1),
                "cost": 1000,
                "tooltip": "Increases all building's CPS by 10%!",
                "name": "Faster Computers"
            },
            "2": {
                "targets": "buildings",
                "unlocked": False,
                "args": ("normal", 1.1),
                "cost": 1000,
                "tooltip": "Increases all building's CPS by 10%!",
                "name": "Better plugins"
            }
        },

        "achievements": {
            "1": {
                "conditions": "(datetime.now() - player[\"run_start\"]).seconds > 1000",
                "name": "test achievement",
                "unlocked": False,
                "tooltip": ""
            },
            "2": {
                "conditions": "(datetime.now() - player[\"run_start\"]).seconds > 1",
                "name": "test achievement",
                "unlocked": False,
                "tooltip": ""
            }
        },

        "tips": [
            f"0.1 + 0.2 = {0.1 + 0.2}",
            "The game saves when you quit",
            "You can check out more\nof my code on GitHub:\ngithub.com/AbnormalNormality",
            "While offline, you generate 25% of\nyou normal CPS",
            "You can press C to open the toolbox",
            "If enabled, the game will autosave every 2 minutes",
            "You can buy buildings and upgrades using the number keys",
            "Press G to open the patch notes",
            "Press F to make the game show ontop of other apps"
        ]
    }

    if not new_game:
        if exists("save_file.txt") and open("save_file.txt", "r").read().strip():
            try:
                try:
                    save_file = loads(b64decode(open("save_file.txt", "r").read().encode("utf-8")).decode("utf-8"))

                except UnicodeDecodeError:
                    save_file = loads(open("save_file.txt", "r").read())

                # noinspection PyTypeChecker
                save_file["run_start"] = datetime.fromisoformat(save_file["run_start"])
                save_file["last_on"] = datetime.fromisoformat(save_file["last_on"])

                save_file["money"] = Decimal(save_file["money"])
                save_file["total_money"] = Decimal(save_file["total_money"])

                save_file["cpc_bonus"] = Decimal(save_file["cpc_bonus"])

            except Error:
                load(True)
                return
        else:
            load(True)
            return

        for b in ["mods"]:
            if b not in save_file:
                save_file[b] = player[b]

        for b in save_file:
            if b in ["cheater", "money", "total_money", "run_start", "last_on", "user_id", "cps_speed", "cpc_bonus",
                     "online", "redeemed_codes", "event_bonus"]:
                player[b] = save_file[b]

        for b in ["buildings", "upgrades", "achievements", "mods"]:
            for c in save_file[b].copy():
                if c not in player[b]:
                    del save_file[b][c]

        for b in save_file["buildings"]:
            player["buildings"][b]["owned"] = save_file["buildings"][b]["owned"]

        for b in save_file["upgrades"]:
            player["upgrades"][b]["unlocked"] = save_file["upgrades"][b]["unlocked"]

        for b in save_file["achievements"]:
            player["achievements"][b]["unlocked"] = save_file["achievements"][b]["unlocked"]

        for b in range(0, (datetime.now() - player["last_on"]).seconds):
            main.after_idle(lambda: update_money(total_cps() * 0.25))

        player["last_on"] = datetime.now()
        player["last_check"] = datetime.now()

    main.title(f"PyClicker {" CHEATER" * 100 if player["cheater"] else ""}")


load()
for a in ["buildings", "upgrades"]:
    for name in player[a]:
        if "name" not in player[a][name]:
            player[a][name]["name"] = name

if len(argv) > 1:
    mods = argv[1:]

    # noinspection SpellCheckingInspection
    for a in ["neverclick", "onstrike", "primitive"]:
        if a in mods:
            player["mods"][a] = True


def save(save_and_exit=True):
    if save_and_exit:
        player["last_on"] = datetime.now()

    def serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

        elif isinstance(obj, Decimal):
            return str(obj)

        raise TypeError(f"Type {type(obj)} not serializable")

    open("save_file.txt", "w").write(b64encode(dumps(player, default=serializer, indent=4).encode("utf-8")
                                               ).decode("utf-8"))

    if save_and_exit:
        main.destroy()


main.protocol("WM_DELETE_WINDOW", save)


def get_v(*args):
    if args[0] == "cpc":
        cpc = player["cpc"]

        cpc += floor((get_v("total", "upgrades") + get_v("total", "buildings")) * player["cpc_bonus"])

        for c in player["upgrades"]:
            if player["upgrades"][c]["unlocked"]:
                if "player" in player["upgrades"][c]["targets"] or player["upgrades"][c]["targets"] == "all":
                    args = player["upgrades"][c]["args"]

                    if args[0] == "normal":
                        cpc *= args[1]

        if player["event_bonus"]:
            day, month, year = datetime.now().strftime("%d-%m-%Y").split("-")

            if f"{day}-{month}" in ["18-08", "19-08", "23-08", "23-08"]:
                cpc *= 2

        return cpc

    if args[0] == "cooldown":
        cooldown = player["cooldown"]

        for c in player["upgrades"]:
            if player["upgrades"][c]["unlocked"]:
                if "player" in player["upgrades"][c]["targets"] or player["upgrades"][c]["targets"] == "all":
                    args = player["upgrades"][c]["args"]
                    if args[0] == "cooldown":
                        cooldown *= args[1]

        return cooldown

    if args[0] == "total":
        if args[1] == "upgrades":
            return len([c for c in player["upgrades"] if player["upgrades"][c]["unlocked"]])

        if args[1] == "buildings":
            return sum([player["buildings"][c]["owned"]for c in player["buildings"]])


def total_cps(buildings=None, single=False):
    t_cps = 0
    buildings_cps = {}

    day, month, year = datetime.now().strftime("%d-%m-%Y").split("-")

    for c in player["upgrades"]:
        for b in player["buildings"]:
            if buildings is not None and (b not in buildings or b != buildings):
                continue

            current = player["buildings"][b]["cps"] * player["buildings"][b]["owned"] if not single else 0

            if b not in buildings_cps:
                buildings_cps[b] = current

            if player["upgrades"][c]["unlocked"]:
                if b in player["upgrades"][c]["targets"] or player["upgrades"][c]["targets"] in ["all", "buildings"]:
                    args = player["upgrades"][c]["args"]
                    if args[0] == "normal":
                        buildings_cps[b] *= args[1]

    for b in buildings_cps:
        if player["event_bonus"]:
            if f"{day}-{month}" in ["18-08", "19-08", "23-08", "23-08"]:
                buildings_cps[b] *= 2

        t_cps += buildings_cps[b]

    return t_cps


# noinspection PyTypeChecker
def update_money(amount, set_money=False):
    player["money"] = Decimal(player["money"]) + Decimal(amount) if not set_money else max(Decimal(amount), 0)
    player["total_money"] += max(0, Decimal(amount))
    player["highscore"] += max(0, Decimal(amount))
    update_ui()


def idle(first=False, loop=True):
    if loop:
        if hasattr(idle, "after_id") and idle.after_id:
            main.after_cancel(idle.after_id)

        idle.after_id = main.after(ceil(1000 / player["cps_speed"]), idle)

    if first:
        update_ui()
        return

    update_money(total_cps() / player["cps_speed"])

    for b in player["achievements"]:
        if eval(player["achievements"][b]["conditions"]) and not player["achievements"][b]["unlocked"]:
            player["achievements"][b]["unlocked"] = True


splash = Label(text=f"P {choice(["y", "i", "i e"])} C l i c k e r", font=("Lucida Fax", 11, "italic"))
splash.pack(pady=5)
"rb.gy/mjm3rm"
create_tooltip(splash, text=f"{" ".join(player["version"])}", x_offset=0,
               y_offset=30)

left = Frame()
left.pack(side="left", fill="both", expand=True)
left.pack_propagate(False)

right_main = Frame()
right_main.pack(side="right", fill="both", expand=True)
right_main.pack_propagate(False)

view_frame = Frame(right_main)
view_frame.pack(side="top", fill="x", pady=(0, 5))

right = Frame(right_main)
right.pack(side="top", fill="both", expand=True)
right.pack_propagate(False)

quick_stats = Label(left)
quick_stats.pack()

stats_label = Label()


def update_ui():
    quick_stats.configure(text=f"${shorten_number(floor(player["money"]))}  |  ${shorten_number(total_cps())}/s")
    if right_view.get() == "s":
        stats_label.configure(text=f"""
__________________________________________

{"(#1) " if player["online"]["lr_holder"] else ""}Your current run has been going for {time_to_units(
            (datetime.now() - player["run_start"]).seconds)["value"]} {time_to_units((datetime.now() - 
                                                                                      player["run_start"]).seconds)[
                                                                                      "units"]}
You've been playing for {time_to_units((datetime.now() - player["last_on"]).seconds)["value"]} {
                             time_to_units((datetime.now() - player["last_on"]).seconds)["units"]}
__________________________________________

Current money: ${floor(player["money"])}
    {"(#1) " if player["online"]["hs_holder"] else ""}Total money: ${floor(player["total_money"])}
    
Total buildings: {get_v("total", "buildings")}
Total upgrades: {get_v("total", "upgrades")}
CPC bonus: {round((get_v("total", "buildings") + get_v("total", "upgrades")) * player["cpc_bonus"], 2)}

{"(#1) " if player["online"]["ma_holder"] else ""}Achievements: {len([b for b in player["achievements"] if player["achievements"][b]["unlocked"]])}/{len(player["achievements"])} ({0 if len([b for b in player["achievements"] if player["achievements"][b]["unlocked"]]) == 0 else round(len([b for b in player["achievements"] if player["achievements"][b]["unlocked"]]) / len(player["achievements"]) * 100, 1)}%)
""".lstrip("\n").rstrip("\n"))

    elif right_view.get() == "b" and mass_buy.get() == "Max":
        if player["cps_speed"] <= 1:
            update_interval = timedelta(seconds=1)
        else:
            # update_interval = timedelta(seconds=player["cps_speed"])
            update_interval = timedelta(seconds=5)

        if datetime.now() - player["last_check"] >= update_interval:
            update_buildings()
            player["last_check"] = datetime.now()


def player_button_press():
    global last_player_button_press

    if (datetime.now() - last_player_button_press).microseconds / 1000 < get_v("cooldown"):
        return

    last_player_button_press = datetime.now()

    update_money(get_v("cpc"))

    main.unbind("<KeyPress-space>")


last_player_button_press = datetime.now()

# noinspection SpellCheckingInspection
image = ImageTk.PhotoImage(Image.open(BytesIO(b64decode(CONSTANT.IMAGE))).resize((150, 150)))
# noinspection PyTypeChecker
player_button = Button(left, image=image, command=player_button_press, state="normal" if not player["mods"]["neverclick"] else "disabled")
player_button.pack(side="top", expand=True)
if not player["mods"]["neverclick"]:
    main.bind("<KeyPress-space>", lambda event=None: player_button_press())
    main.bind("<KeyRelease-space>", lambda event=None: main.bind("<KeyPress-space>", lambda event1=None:
              player_button_press()))


def toolbox(dev=False):
    global player

    if dev:
        tool_num = simpledialog.askinteger("Dev",
                                           "What tool do you want to use?\n1: Decode/encode savefile\n2: Set money"
                                           "\n3: See all cloud variables")

        if tool_num is None:
            return

        if tool_num == 1:
            player["cheater"] = True
            allow_save_editing()

        elif tool_num == 2:
            player["cheater"] = True
            amount = simpledialog.askinteger("Dev", "How much money do you want?")
            if amount is not None:
                update_money(amount, True)

        elif tool_num == 3:
            cloud_vars = manage_variable(CONSTANT.CRED_PATH, CONSTANT.DATABASE_URL, upload=False)
            messagebox.showinfo("Dev", "\n".join([f"{b}: {cloud_vars[b]}" for b in cloud_vars]))

    else:
        tool_num = simpledialog.askinteger("Toolbox", f"What tool do you want to use?\n1: Restart\n2: "
                                                      f"{"Disable" if player["autosave"] else "Enable"} autosave\n"
                                                      f"3: Change CPS speed\n4: Redeem code")

        if tool_num is None:
            return

        elif tool_num == 1:
            if messagebox.askyesno("Reset", "Are you sure you want to delete all save data?\nYou may "
                                            "need to close and reopen the app after"):
                load(True)
                idle(True)
                update_buildings()

        elif tool_num == 2:
            player["autosave"] = not player["autosave"]
            if player["autosave"]:
                schedule_autosave()

        elif tool_num == 3:
            min_ = 0.1
            max_ = 20
            speed = simpledialog.askfloat("CPS speed", f"How fast do you want the CPS to be?\nMin {min_}, max "
                                                       f"{max_}\nHigh speeds may cause errors",
                                          initialvalue=player["cps_speed"])
            if speed is not None or 0:
                player["cps_speed"] = min(max(speed, min_), max_)

        elif tool_num == 4:
            code = ""
            loop = False

            day, month, year = map(int, datetime.now().strftime("%d-%m-%Y").split("-"))

            while code is not None:
                code = simpledialog.askstring("Redeem code", f"{f"Already redeemed code {code}\n" if code in player["redeemed_codes"] else f"Unrecognised code {code}\n" if loop else ""}Input the code you want to redeem?")
                loop = True

                if (code == "AL1A1S3P1C" and code not in player["redeemed_codes"] and
                        year == 2024 and month in range(8, 13) and day in range(1, 32)):
                    is_code = True
                    update_money(10000000)

                else:
                    is_code = False

                if is_code:
                    player["redeemed_codes"].append(code)
                    break



main.bind("<Control-Shift-C>", lambda event=None: toolbox(True))
main.bind("<c>", lambda event=None: toolbox())

right_view = StringVar(value="b")
# noinspection SpellCheckingInspection
tabs = ["build-", "upgra-", "stats"]
for a in tabs:
    Radiobutton(view_frame, text=a.capitalize(), variable=right_view, value=a[0], command=lambda: update_buildings(),
                ).pack(side="left", expand=True)
    main.bind(f"<{a[0]}>", lambda event, tab=a[0]: exec(f"right_view.set(\"{tab}\")\nupdate_buildings()"))

mass_buy = StringVar(value="1")
tip = choice(player["tips"])


# noinspection SpellCheckingInspection
def update_buildings(building=None):
    global tip, stats_label

    if right_view.get() == "b":
        if building is not None:
            if mass_buy.get() != "Max":
                count = int(mass_buy.get())
                cost = sum(
                    ceil(player["buildings"][building]["cost"] * 1.05 ** (player["buildings"][building]["owned"] + i))
                    for i in range(count)
                )
            else:
                cost = 0
                count = 0
                building_cost = ceil(
                    player["buildings"][building]["cost"] * 1.05 ** player["buildings"][building]["owned"])
                money = player["money"]

                while money >= building_cost:
                    money -= building_cost
                    cost += building_cost
                    count += 1
                    building_cost = ceil(player["buildings"][building]["cost"] * 1.05 ** (
                                player["buildings"][building]["owned"] + count))

            if player["money"] >= cost:
                player["money"] -= cost
                player["buildings"][building]["owned"] += count

                update_ui()
            else:
                return

    elif right_view.get() == "u":
        if building is not None and player["money"] >= player["upgrades"][building]["cost"]:
            player["money"] -= player["upgrades"][building]["cost"]
            player["upgrades"][building]["unlocked"] = True

            update_ui()

    [w.destroy() for w in right.winfo_children()]

    if right_view.get() == "b":
        frame = Frame(right)
        frame.pack(pady=(0, 5))

        Label(frame, text="Buy").pack(side="left")

        values = ["1", "5", "10", "25", "50", "100", "Max"]

        OptionMenu(frame, mass_buy, mass_buy.get(), *values,
                   command=lambda event: update_buildings()).pack(side="left", padx=(5, 0))

        scrolling_frame = create_scrollable_frame(right)

        keys = "1234567890qwerty"
        key_index = 0

        def set_amount(c):
            mass_buy.set(values[c])
            update_buildings()

        for _ in values:
            if key_index >= len(keys) and key_index >= len(values):
                break
            main.unbind(f"<Control-Key-{keys[key_index]}>")
            main.bind(f"<Control-Key-{keys[key_index]}>", lambda event, c=key_index: set_amount(c))
            key_index += 1

        key_index = 0

        for b in dict(sorted(player["buildings"].items(), key=lambda item: item[1]["cost"])):
            frame = Frame(scrolling_frame)
            frame.pack(side="top")

            button = Button(frame, text=f"({player["buildings"][b]["owned"]}) {
                            player["buildings"][b]["name"].capitalize()}", command=lambda c=b: update_buildings(c),
                            state="normal" if not player["mods"]["onstrike"] else "disabled")
            button.pack(side="left")

            if mass_buy.get() != "Max":
                cost = sum(ceil(player["buildings"][b]["cost"] * 1.05 ** (player["buildings"][b]["owned"] + i))
                           for i in range(int(mass_buy.get())))
                count = int(mass_buy.get())
            else:
                cost = 0
                count = 0
                current_money = player["money"]

                while current_money >= ceil(
                        player["buildings"][b]["cost"] * 1.05 ** (player["buildings"][b]["owned"] + count)):
                    building_cost = ceil(
                        player["buildings"][b]["cost"] * 1.05 ** (player["buildings"][b]["owned"] + count))
                    cost += building_cost
                    current_money -= building_cost
                    count += 1

            Label(frame, text=f"${shorten_number(cost)}{f" ({count})" if count != 1 else ""}").pack(side="left", padx=(
                5, 0))

            tooltip = f"Earning ${shorten_number(total_cps(b))}/s ("f"{floor(total_cps(b) / total_cps() * 100
                                                                             ) if total_cps(b) != 0 else 0}%)"

            create_tooltip(button, text=tooltip if "tooltip" not in player["buildings"][b] else f"{
                           tooltip}\n{player["buildings"][b]["tooltip"]}", wait_time=100, x_offset=122, y_offset=1)

            if key_index < len(keys):
                key = keys[key_index]
                main.unbind(f"<Key-{key}>")
                if not player["mods"]["onstrike"]:
                    main.bind(f"<Key-{key}>", lambda event, c=b: update_buildings(c))
                    key_index += 1

    elif right_view.get() == "u":
        def buy_all():
            for c in dict(sorted(player["upgrades"].items(), key=lambda item: item[1]["cost"])):
                if player["upgrades"][c]["unlocked"]:
                    continue

                if player["money"] < player["upgrades"][c]["cost"]:
                    break

                player["money"] -= player["upgrades"][c]["cost"]
                player["upgrades"][c]["unlocked"] = True

            update_ui()
            update_buildings()

        Button(right, text="Buy all", command=buy_all, state="normal" if not player["mods"]["onstrike"] else "disabled").pack(pady=(0, 5))

        scrolling_frame = create_scrollable_frame(right)

        keys = "1234567890qwerty"
        key_index = 0

        for b in dict(sorted(player["upgrades"].items(), key=lambda item: item[1]["cost"])):
            if player["upgrades"][b]["unlocked"] is True:
                continue

            frame = Frame(scrolling_frame)
            frame.pack(side="top")

            button = Button(frame, text=player["upgrades"][b]["name"].capitalize(), command=lambda c=b:
                            update_buildings(c), state="normal" if not player["mods"]["onstrike"] else "disabled")
            button.pack(side="left")

            Label(frame, text=f"${shorten_number(player["upgrades"][b]["cost"])}").pack(side="left", padx=(5, 0))

            create_tooltip(button, text=f"{player["upgrades"][b]["targets"] if player["upgrades"][b]["targets"] is str 
                                           else ", ".join(player["upgrades"][b]["targets"] if 
                                                          player["upgrades"][b]["targets"] != "all" else c for c in 
                                                          list(player["buildings"]) + ["Player"])} yield increased {
                                           player["upgrades"][b]["args"][1]
            }x" if "tooltip" not in player["upgrades"][b] else player["upgrades"][b]["tooltip"], wait_time=100,
                           x_offset=122, y_offset=1)

            if key_index < len(keys):
                key = keys[key_index]
                main.unbind(f"<Key-{key}>")
                if not player["mods"]["primitive"]:
                    main.bind(f"<Key-{key}>", lambda event, c=b: update_buildings(c))
                    key_index += 1

    elif right_view.get() == "s":
        scrolling_frame = create_scrollable_frame(right)

        def randomise_tip():
            global tip
            tip = choice([c for c in player["tips"] if c != tip])
            tip_label.configure(text=tip)

        tip_label = Label(scrolling_frame, text=tip, wraplength=right.winfo_width())
        tip_label.pack(pady=(0, 5))

        Button(scrolling_frame, command=randomise_tip, text="New Tip").pack()

        stats_label = Label(scrolling_frame, wraplength=right.winfo_width() - 20)
        stats_label.pack()

        def view_achievements():
            modal = Toplevel()
            resize_window(modal, 4, 4, False)
            modal.focus_force()
            modal.bind("<FocusOut>", lambda event: modal.destroy())

            modal_scrolling_frame = create_scrollable_frame(modal)

            for c in player["achievements"]:
                label = Label(modal_scrolling_frame, text=f"{c}{" (Unlocked)" if player["achievements"][c]["unlocked"] else ""}", anchor="w", bg="#e0e0e0")
                label.pack(pady=(5 if list(player["achievements"]).index(c) == 0 else 0, 5), padx=5, fill="x", expand=True)
                if "tooltip" in player["achievements"][c]:
                    create_tooltip(label, player["achievements"][c]["tooltip"], y_offset=30, x_offset=5, wait_time=0)

        Button(scrolling_frame, command=view_achievements, text="View achievements").pack(pady=5)

        Button(scrolling_frame, command=lambda: main.clipboard_append(player["user_id"]), text="Copy UUID").pack(pady=(0, 10))

        update_ui()


def schedule_autosave(first=True):
    if not player["autosave"]:
        return

    if hasattr(schedule_autosave, "after_id") and schedule_autosave.after_id:
        main.after_cancel(schedule_autosave.after_id)

    schedule_autosave.after_id = main.after(120000, lambda event=None: schedule_autosave(False))

    if first:
        return

    save(False)


def fb_shortcut(key, value=None, upload=False):
    return manage_variable(CONSTANT.CRED, CONSTANT.DATABASE_URL, key, value, upload)


def update_database():
    if hasattr(update_database, "after_id") and update_database.after_id:
        main.after_cancel(update_database.after_id)

    update_database.after_id = main.after(600000, update_database)

    def task():
        try:
            cloud_vars = manage_variable(CONSTANT.CRED_PATH, CONSTANT.DATABASE_URL, upload=False)

            # Global highscore
            if "global_highscore" not in cloud_vars or (fb_shortcut("global_highscore") < float(player["highscore"]) and not player["cheater"]):  # noqa: E501
                fb_shortcut("global_highscore", float(player["highscore"]), True)

                if "gh_holder" not in cloud_vars or fb_shortcut("gh_holder") != player["user_id"]:
                    fb_shortcut("gh_holder", player["user_id"], True)

            player["online"]["hs_holder"] = fb_shortcut("gh_holder") == player["user_id"]

            # Longest run
            if "longest_run" not in cloud_vars or ((datetime.now() - datetime.fromisoformat(fb_shortcut("longest_run"))).seconds < (datetime.now() - player["run_start"]).seconds and not player["cheater"]):  # noqa: E501
                fb_shortcut("longest_run", datetime.isoformat(player["run_start"]), True)

                if "lr_holder" not in cloud_vars or fb_shortcut("lr_holder") != player["user_id"]:
                    fb_shortcut("lr_holder", player["user_id"], True)

            player["online"]["lr_holder"] = fb_shortcut("lr_holder") == player["user_id"]

            # Longest run
            if "most_achievements" not in cloud_vars or len([b for b in player["achievements"] if player["achievements"][b]["unlocked"]]) > fb_shortcut("most_achievements"):  # noqa: E501
                fb_shortcut("most_achievements", len([b for b in player["achievements"] if player["achievements"][b]["unlocked"]]), True)

                if "ma_holder" not in cloud_vars or fb_shortcut("ma_holder") != player["user_id"]:
                    fb_shortcut("ma_holder", player["user_id"], True)

            player["online"]["ma_holder"] = fb_shortcut("ma_holder") == player["user_id"]

        except (TransportError, UnavailableError):
            pass

    Thread(target=task).start()


main.bind("<g>", lambda event: w_open("https://github.com/AbnormalNormality/PyClicker/releases/latest"))
main.bind("<Control-Shift-G>", lambda event: w_open("https://console.firebase.google.com/project/pyclicker/database/pyclicker-default-rtdb/data"))  # noqa: E501


def toggle_on_top():
    if main.attributes("-topmost"):
        main.attributes("-topmost", False)
        main.overrideredirect(False)
    else:
        main.attributes("-topmost", True)
        main.overrideredirect(True)


main.bind("<f>", lambda event: toggle_on_top())

schedule_autosave()
main.after(1000, update_database)
update_buildings()
idle(first=True)
update_bg(main)

main.mainloop()
