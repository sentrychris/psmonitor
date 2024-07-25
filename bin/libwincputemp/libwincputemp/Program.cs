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

        static void Main()
        {
            computer.Open();
            GetCpuTemperature();
            Environment.Exit(0);
        }

        private static void GetCpuTemperature()
        {
            foreach (IHardware hardware in computer.Hardware)
            {
                hardware.Update();
            }

            ISensor cpuSensor = GetCpuPackageTemperatureSensor();

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
    }
}