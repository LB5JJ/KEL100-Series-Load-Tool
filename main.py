import os
import argparse
import time
import signal
import matplotlib.pyplot as plt

import help
from load import Load

stop = False
args = None

def sigint(signum, frame):
    global stop
    if args.command.lower() == "battery-test":
        stop = True
    else:
        exit(0)

def main() -> None:
    global args

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
        match args.command.lower():
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
            
            case "constant-voltage":
                if args.argument is None:
                    help(command="constant-voltage", error="Missing argument")
                load.cv = float(args.argument)
                load.mode = Load.Mode.CV

            case "constant-current":
                if args.argument is None:
                    help(command="constant-current", error="Missing argument")
                load.cc = float(args.argument)
                load.mode = Load.Mode.CC

            case "constant-resistance":
                if args.argument is None:
                    help(command="constant-resistance", error="Missing argument")
                load.cr = float(args.argument)
                load.mode = Load.Mode.CR

            case "constant-power":
                if args.argument is None:
                    help(command="constant-power", error="Missing argument")
                load.cp = float(args.argument)
                load.mode = Load.Mode.CP

            case "battery-test":
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

                    while not stop:
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

            case _:
                help.main()

    exit(0)

if __name__ == '__main__':
    main()