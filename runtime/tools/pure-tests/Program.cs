using System;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using NUnit.Framework;

internal static class Program
{
    private static int Main()
    {
        // Narrow standalone runner for this fixture's eight synchronous [Test]
        // methods. This does NOT emulate Unity callbacks or its test runner.
        var type = typeof(CriticalShift.Tests.EditMode.ProcessLifetimeTests);
        var methods = type.GetMethods().Where(m => m.IsDefined(typeof(TestAttribute), false)).ToArray();
        if (methods.Length != 8 || methods.Any(m => m.GetParameters().Length != 0 || m.ReturnType != typeof(void)))
            throw new InvalidOperationException("Standalone fixture discovery changed; review this harness.");
        int failed = 0;
        foreach (var method in methods.OrderBy(m => m.Name))
        {
            try
            {
                method.Invoke(Activator.CreateInstance(type), null);
                Console.WriteLine("PASS " + type.FullName + "." + method.Name);
            }
            catch (TargetInvocationException ex)
            {
                failed++;
                Console.WriteLine("FAIL " + method.Name + ": " + ex.InnerException);
            }
        }
        Console.WriteLine(JsonSerializer.Serialize(new
        {
            runner = "Standalone .NET 8 assertion harness; NOT Unity EditMode",
            nunit = typeof(Assert).Assembly.FullName,
            discovered = methods.Length, executed = methods.Length,
            passed = methods.Length - failed, failed, skipped = 0
        }));
        return failed == 0 ? 0 : 1;
    }
}
