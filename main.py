import os
import argparse
import time
import signal
import matplotlib.pyplot as plt

import help
from load import Load

def main() -> None:
    stop = False

    def sigint(signum, frame):
        if args.command.lower() == "battery-test":
            nonlocal stop
            stop = True
        else:
            exit(0)

    signal.signal(signal.SIGINT, sigint)

    parser = argparse.ArgumentParser(description = "KORAD Electronic Load Utility")
    parser.add_argument("command", nargs='?', default="help")
    parser.add_argument("argument", nargs='?')
    parser.add_argument("--serial-port", default=os.environ.get('SERIAL_PORT'))
    parser.add_argument("--serial-speed", type=int)
    parser.add_argument("--cutoff-voltage", type=float)
    parser.add_argument("--cutoff-seconds", type=int)
    parser.add_argument("--no-cutoff", action="store_true")
    parser.add_argument("--constant-current", type=float)
    parser.add_argument("--constant-power", type=float)
    parser.add_argument("--sampling-interval", type=float, default=5)
    parser.add_argument("--file-base-name", type=str, default="report")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    env_serial_speed = os.environ.get('SERIAL_SPEED')

    if args.serial_speed is None:
        args.serial_speed = int(env_serial_speed) if env_serial_speed else 115200

    with Load(args.serial_port, args.serial_speed) as load:
        command = args.command.lower()

        match command:
            case "help":
                help.main(args.argument)

            case "ports":
                help.ports()

            case "id":
                print(load.id)

            case "enable":
                load.enabled = True

            case "disable":
                load.enabled = False

            case "status":
                status(load)
            
            case "constant-voltage" | "constant-current" | "constant-resistance" | "constant-power":
                mode(load, command, args.argument)

            case "battery-test":
                battery_test(load, args, lambda : stop)

            case _:
                help.main()

    exit(0)

def mode(load, mode, arg):
    if arg is None:
        help(command=mode, error="Missing argument")

    match mode:
        case "constant-voltage":
            load.cv = float(args.argument)
            load.mode = Load.Mode.CV

        case "constant-current":
            load.cc = float(args.argument)
            load.mode = Load.Mode.CC

        case "constant-resistance":
            load.cr = float(args.argument)
            load.mode = Load.Mode.CR

        case "constant-power":
            load.cp = float(args.argument)
            load.mode = Load.Mode.CP


def status(load):
    state = "(On)" if load.enabled else "(Off)"

    match load.mode:
        case Load.Mode.CV:
            print(f"Constant Voltage: {load.cv} V {state}")
        case Load.Mode.CC:
            print(f"Constant Current: {load.cc} A {state}")
        case Load.Mode.CR:
            print(f"Constant Resistance: {load.cr} Ω {state}")
        case Load.Mode.CP:
            print(f"Constant Power: {load.cp} W {state}")
                
    print(f"Voltage: {load.voltage} V")
    print(f"Current: {load.current} A")
    print(f"  Power: {load.power} W")


def battery_test(load, args, stopped):
    if args.constant_current and args.constant_power is None:
        load.cc = float(args.constant_current)
        load.mode = Load.Mode.CC
    elif args.constant_power and args.constant_current is None:
        load.cp = float(args.constant_power)
        load.mode = Load.Mode.CP
    else:
        help.main(command="battery-test", error="Must supply exactly one of --constant-current or --constant-power")

    if args.cutoff_voltage is None and args.cutoff_seconds is None and not args.no_cutoff:
        help.main(command="battery-test", error="Must supply at least one of --cutoff-voltage, --cutoff-seconds or --no-cutoff")

    print(args)

    with open(args.file_base_name + ".csv", "w") as csv:
        second = []
        volt = []

        coulombs = 0
        joules = 0

        csv.write("elapsed,voltage,current,power\n")

        start = int(time.time())

        load.enabled = True

        ampere_hours = 0
        watt_hours = 0

        while not stopped():
            runtime = int(time.time()) - start

            voltage = load.voltage
            current = load.current
            power = load.power

            second.append(runtime)
            volt.append(voltage)

            coulombs += current * args.sampling_interval
            joules += power * args.sampling_interval

            ampere_hours = coulombs / 3600
            watt_hours = joules / 3600

            if args.verbose:
                print(f"{runtime} s: {voltage} V, {current} A, {power} W, {ampere_hours:.2f} Ah, {watt_hours:.2f} Wh    ", end="\r")

            csv.write(f"{runtime},{voltage},{current},{power}\n")
        
            if args.cutoff_voltage and args.cutoff_voltage > voltage:
                break

            if args.cutoff_seconds and runtime > args.cutoff_seconds:
                break

            time.sleep(args.sampling_interval)

        load.enabled = False

        figur, axis = plt.subplots()

        title_mode = f"Constant {'Current' if args.constant_current else 'Power'}"
        title_rate = f"{args.constant_current} A" if args.constant_current else f"{args.constant_power} W"
        title_ampere_hours = f"{ampere_hours:.2f} Ah" if ampere_hours >= 1 else f"{int(ampere_hours*1000)} mAh"
        title_watt_hours = f"{watt_hours:.2f} Wh" if watt_hours >= 1 else f"{int(watt_hours*1000)} mWh"

        axis.set_ylabel("Volt")
        axis.set_xlabel("Seconds")
        axis.set_title(f"{title_mode} {title_rate}: {title_ampere_hours}, {title_watt_hours}")

        axis.plot(second, volt)

        plt.grid(linestyle=":")

        plt.savefig(args.file_base_name + ".png")

        if args.verbose:
            print("")


if __name__ == '__main__':
    main()