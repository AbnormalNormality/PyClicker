from tkinter import Tk, Label, Frame, simpledialog, messagebox, StringVar
from PIL import ImageTk, Image
from base64 import b64encode, b64decode
from json import dumps, loads
from os.path import exists
from binascii import Error
from random import choice
from math import ceil, floor
from copy import deepcopy
from tkinter.ttk import Button, Radiobutton, OptionMenu
from datetime import datetime
from decimal import Decimal

from AliasTkFunctions import fix_resolution_issue, resize_window, create_scrollable_frame, update_bg, create_tooltip
from AliasGeneralFunctions import shorten_number, time_to_units

from dev_tools import *

fix_resolution_issue()

main = Tk()
resize_window(main, 3, 3, False)

player = {}


def load(new_game=False):
    global player
    default_player = {
        # flags
        "cheater": False,
        "autosave": True,

        "version": "0.1",
        "version_notes": f"The (released) alpha\ngithub",  # noqa: E501

        # values
        "money": 0,
        "total_money": 0,

        "cpc": 1,

        # time related
        "run_start": datetime.now(),
        "last_on": datetime.now(),

        # buildings and upgrades
        "buildings": {
            "1": {
                "cost": 10,
                "owned": 0,
                "cps": 0.1
            },

            "2": {
                "cost": 100,
                "owned": 0,
                "cps": 1,
            },

            "3": {
                "cost": 1000,
                "owned": 0,
                "cps": 10,
            }
        },

        "upgrades": {
            "Global increase": {
                "targets": "all",
                "unlocked": False,
                "args": ("normal", 1.2),  # (type, type-specific args)
                "cost": 100
            }
        }
    }

    if new_game:
        player = deepcopy(default_player)
        player["run_start"] = datetime.now()

    else:
        player = deepcopy(default_player)

        if exists("save_file.txt") and open("save_file.txt", "r").read().strip():
            try:
                save_file = loads(b64decode(open("save_file.txt", "r").read().encode("utf-8")).decode("utf-8"))

                # noinspection PyTypeChecker
                save_file["run_start"] = datetime.fromisoformat(save_file["run_start"])
                save_file["last_on"] = datetime.fromisoformat(save_file["last_on"])

                save_file["money"] = Decimal(save_file["money"])
                save_file["total_money"] = Decimal(save_file["total_money"])
            except Error:
                load(True)
                return
        else:
            load(True)
            return

        for b in save_file:
            if b in ["cheater", "money", "total_money", "run_start", "last_on"]:
                player[b] = save_file[b]

        for b in save_file["buildings"]:
            player["buildings"][b]["owned"] = save_file["buildings"][b]["owned"]

        for b in save_file["upgrades"]:
            player["upgrades"][b]["unlocked"] = save_file["upgrades"][b]["unlocked"]

        for b in range(0, (datetime.now() - player["last_on"]).seconds):
            main.after_idle(lambda: update_money(total_cps() * 0.25))

        player["last_on"] = datetime.now()


load()

main.title(f"PyClicker{" CHEATER" * 100 if player["cheater"] else ""}")


def save(save_and_exit=True):
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


def total_cps(buildings=None, single=False):
    t_cps = 0

    for b in player["buildings"]:
        if buildings is not None and (b not in buildings or b != buildings):
            continue

        current = player["buildings"][b]["cps"] * player["buildings"][b]["owned"] if not single else 0

        for c in player["upgrades"]:
            if player["upgrades"][c]["unlocked"]:
                if b in player["upgrades"][c]["targets"] or player["upgrades"][c]["targets"] == "all":
                    args = player["upgrades"][c]["args"]
                    if args[0] == "normal":
                        current *= args[1]

        t_cps += current

    return t_cps


# noinspection PyTypeChecker
def update_money(amount, set_money=False):
    player["money"] = Decimal(player["money"]) + Decimal(amount) if not set_money else Decimal(amount)
    player["total_money"] += max(0, Decimal(amount))
    update_ui()


def idle(first=False, loop=True):
    if loop:
        if hasattr(idle, "after_id") and idle.after_id:
            main.after_cancel(idle.after_id)

        idle.after_id = main.after(1000, idle)

    if first:
        update_ui()
        return

    update_money(total_cps())


splash = Label(text=f"P {choice(["y", "i", "i e"])} C l i c k e r", font=("Lucida Fax", 11, "italic"))
splash.pack(pady=5)

create_tooltip(splash, text=f"{player["version"]}\n{player["version_notes"]}", x_offset=0,
               y_offset=30, wrap_length=500)

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
    global stats_label
    quick_stats.configure(text=f"${shorten_number(floor(player["money"]))}  |  ${shorten_number(total_cps())}/s")
    if right_view.get() == "s":
        stats_label.configure(text=f"""
__________________________________________

Your current run has been going for {time_to_units((datetime.now() - player["run_start"]).seconds)["value"]} {
                                     time_to_units((datetime.now() - player["run_start"]).seconds)["units"]}
You've been playing for {time_to_units((datetime.now() - player["last_on"]).seconds)["value"]} {
                         time_to_units((datetime.now() - player["last_on"]).seconds)["units"]}
__________________________________________

Current money: ${floor(player["money"])}
Total money: ${floor(player["total_money"])}
""".lstrip("\n").rstrip("\n"))


def player_button_press():
    global last_player_button_press

    if (datetime.now() - last_player_button_press).microseconds / 1000 < 75:
        return

    last_player_button_press = datetime.now()

    cpc = player["cpc"]

    for c in player["upgrades"]:
        if player["upgrades"][c]["unlocked"]:
            if "player" in player["upgrades"][c]["targets"] or player["upgrades"][c]["targets"] == "all":
                args = player["upgrades"][c]["args"]
                if args[0] == "normal":
                    cpc *= args[1]

    update_money(cpc)

    main.unbind("<KeyPress-space>")


last_player_button_press = datetime.now()

image = ImageTk.PhotoImage(Image.open("python.png").resize((150, 150)))
# noinspection PyTypeChecker
player_button = Button(left, image=image, command=player_button_press, takefocus=False)
player_button.pack(side="top", expand=True)
main.bind("<KeyPress-space>", lambda event=None: player_button_press())
main.bind("<KeyRelease-space>", lambda event=None: main.bind("<KeyPress-space>", lambda event1=None:
          player_button_press()))


def toolbox(dev=False):
    global player

    if dev:
        tool_num = simpledialog.askinteger("Dev",
                                           "What tool do you want to use?\n1: Decode/encode savefile\n2: Set money")
        if tool_num is None:
            return

        player["cheater"] = True

        if tool_num == 1:
            allow_save_editing()

        if tool_num == 2:
            amount = simpledialog.askinteger("Dev", "How much money do you want?")
            if amount is not None:
                update_money(amount, True)

    else:
        tool_num = simpledialog.askinteger("Toolbox", f"What tool do you want to use?\n1: Restart\n2: "
                                                      f"{"Disable" if player["autosave"] else "Enable"} autosave")

        if tool_num == 1:
            if messagebox.askyesno("Reset", "Are you sure you want to delete all save data?\nYou may "
                                            "need to close and reopen the app after"):
                load(True)
                idle(True)
                update_buildings()

        if tool_num == 2:
            player["autosave"] = not player["autosave"]
            if player["autosave"]:
                schedule_autosave()


main.bind("<Control-Shift-C>", lambda event=None: toolbox(True))
main.bind("<c>", lambda event=None: toolbox())

right_view = StringVar(value="b")
# noinspection SpellCheckingInspection
for a in ["build-", "upgra-", "stats"]:
    Radiobutton(view_frame, text=a.capitalize(), variable=right_view, value=a[0], command=lambda: update_buildings(),
                takefocus=False).pack(side="left", expand=True)

mass_buy = StringVar(value="1")

tips = [
    f"0.1 + 0.2 = {0.1 + 0.2}",
    "The game saves when you quit",
    "You can check out more\nof my code on GitHub:\ngithub.com/AbnormalNormality",
    "While offline, you generate 25% of\nyou normal CPS",
    "You can press C to open the toolbox",
    "If enabled, the game will autosave every 2 minutes"
]
tip = choice(tips)


# noinspection SpellCheckingInspection
def update_buildings(building=None):
    global tip, stats_label

    [w.destroy() for w in right.winfo_children()]

    if right_view.get() == "b":
        frame = Frame(right)
        frame.pack(pady=(0, 5))

        Label(frame, text="Buy").pack(side="left")

        OptionMenu(frame, mass_buy, mass_buy.get(), *["1", "5", "10", "25", "50", "100", "1000"],
                   command=lambda event: update_buildings()).pack(side="left", padx=(5, 0))

        scrolling_frame = create_scrollable_frame(right)

        if building is not None:
            cost = sum(ceil(player["buildings"][building]["cost"] * 1.05 ** (player["buildings"][building]["owned"] + i)
                            ) for i in range(int(mass_buy.get())))
            if player["money"] >= cost:
                player["money"] -= cost
                for b in range(int(mass_buy.get())):
                    player["buildings"][building]["owned"] += 1

                update_ui()

        keys = "1234567890qwertyuiop"
        key_index = 0

        for b in dict(sorted(player["buildings"].items(), key=lambda item: item[1]["cost"])):
            frame = Frame(scrolling_frame)
            frame.pack(side="top")

            button = Button(frame, text=f"({player["buildings"][b]["owned"]}) {b.capitalize()}", command=lambda c=b:
                            update_buildings(c))
            button.pack(side="left")

            cost = sum(ceil(player["buildings"][b]["cost"] * 1.05 ** (player["buildings"][b]["owned"] + i)
                            ) for i in range(int(mass_buy.get())))
            Label(frame, text=f"${shorten_number(cost)}").pack(side="left", padx=(5, 0))

            tooltip = f"Earning ${shorten_number(total_cps(b))}/s ("f"{floor(total_cps(b) / total_cps() * 100
                                                                             ) if total_cps(b) != 0 else 0}%)"

            create_tooltip(button, text=tooltip if "tooltip" not in player["buildings"][b] else f"{
                           tooltip}\n{player["buildings"][b]["tooltip"]}", wait_time=100, x_offset=122, y_offset=1)

            if key_index < len(keys):
                key = keys[key_index]
                main.unbind(f"<Key-{key}>")
                main.bind(f"<Key-{key}>", lambda event, c=b: update_buildings(c))
                key_index += 1

    elif right_view.get() == "u":
        scrolling_frame = create_scrollable_frame(right)

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

        Button(scrolling_frame, text="Buy all", command=buy_all).pack(pady=(0, 5))

        if building is not None and player["money"] >= player["upgrades"][building]["cost"]:
            player["money"] -= player["upgrades"][building]["cost"]
            player["upgrades"][building]["unlocked"] = True

            update_ui()

        keys = "1234567890qwertyuiop"
        key_index = 0

        for b in dict(sorted(player["upgrades"].items(), key=lambda item: item[1]["cost"])):
            if player["upgrades"][b]["unlocked"] is True:
                continue

            frame = Frame(scrolling_frame)
            frame.pack(side="top")

            button = Button(frame, text=b.capitalize(), command=lambda c=b:
                            update_buildings(c))
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
                main.bind(f"<Key-{key}>", lambda event, c=b: update_buildings(c))
                key_index += 1

    elif right_view.get() == "s":
        scrolling_frame = create_scrollable_frame(right)

        def randomise_tip():
            global tip
            tip = choice([c for c in tips if c != tip])
            tip_label.configure(text=tip)

        tip_label = Label(scrolling_frame, text=tip, wraplength=right.winfo_width())
        tip_label.pack(pady=(0, 5))

        Button(scrolling_frame, command=randomise_tip, text="New Tip", takefocus=False).pack()

        stats_label = Label(scrolling_frame, wraplength=right.winfo_width() - 20)
        stats_label.pack()
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
    print("Autosaved!")


schedule_autosave()
update_buildings()
idle(first=True)
update_bg(main)

main.mainloop()
