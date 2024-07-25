using System;
using System.Linq;
using LibreHardwareMonitor.Hardware;

namespace LibWinCPUTemp
{
    /**
     * A tiny CLI program for obtaining CPU temperature readings using LibreOpenHardwareMonitor's
     * LibreOpenHardwareMonitorLib.dll. PSMonitor depends on this executable to provide a CPU temp
     * value on Windows.
     */
    class Program
    {
        static readonly Computer computer = new Computer()
        {
            IsCpuEnabled = true,
        };

        static void GetCPUTemp()
        {
            foreach (var hardware in computer.Hardware)
            {
                hardware.Update();
            }

            var cpuSensor = GetCpuPackageTemperatureSensor();

            if (cpuSensor != null)
            {
                Console.WriteLine(cpuSensor.Value.GetValueOrDefault());
            } else
            {
                Console.WriteLine("N/A");
            }
        }

        private static ISensor GetCpuPackageTemperatureSensor()
        {
            return computer.Hardware
                .Where(i => i.HardwareType == HardwareType.Cpu)
                .SelectMany(s => s.Sensors)
                .FirstOrDefault(s => {
                    return s.SensorType == SensorType.Temperature && s.Name.Contains("CPU Package");
                });
        }

        static void Main()
        {
            computer.Open();
            GetCPUTemp();
            Environment.Exit(0);
        }
    }
}