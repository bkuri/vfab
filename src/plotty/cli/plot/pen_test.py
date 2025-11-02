"""
Pen test command for ploTTY CLI.
"""

from __future__ import annotations

from typing import Optional
import time

from ...utils import error_handler

try:
    from rich.console import Console

    console = Console()
except ImportError:
    console = None


def test_pen_operation(port: Optional[str] = None, model: int = 1, cycles: int = 3):
    """Test pen operation."""
    try:
        from ...plotting import MultiPenPlotter

        # Initialize plotter
        plotter = MultiPenPlotter(port=port, model=model, interactive=False)

        if console:
            console.print("🖊️  Pen Test")
            console.print("=" * 30)
            console.print(f"📡 Device: {'auto' if port is None else port}")
            console.print(f"🔄 Cycles: {cycles}")
            console.print("")

        # Test basic pen movements
        test_results = {
            "success": True,
            "cycles_completed": 0,
            "errors": [],
            "total_time": 0,
        }

        start_time = time.time()

        for cycle in range(cycles):
            try:
                if console:
                    console.print(f"🔄 Cycle {cycle + 1}/{cycles}")

                # Test pen up/down
                if console:
                    console.print("  📐 Testing pen up/down movement...")

                # Use the device manager to test pen movements
                if hasattr(plotter.manager, "pen_up"):
                    plotter.manager.pen_up()
                    time.sleep(0.5)

                if hasattr(plotter.manager, "pen_down"):
                    plotter.manager.pen_down()
                    time.sleep(0.5)

                # Test small movement pattern
                if console:
                    console.print("  📏 Testing movement pattern...")

                # Create a simple test pattern
                test_moves = [
                    (0, 0),  # Start position
                    (100, 0),  # Move right
                    (100, 100),  # Move up
                    (0, 100),  # Move left
                    (0, 0),  # Return to start
                ]

                for i, (x, y) in enumerate(test_moves):
                    if hasattr(plotter.manager, "move_to"):
                        plotter.manager.move_to(x, y)
                        time.sleep(0.2)

                    if console and i > 0:  # Skip first position
                        console.print(f"    📍 Move to ({x}, {y})")

                test_results["cycles_completed"] += 1

                if console:
                    console.print(f"  ✅ Cycle {cycle + 1} completed", style="green")

                # Small delay between cycles
                if cycle < cycles - 1:
                    time.sleep(1)

            except Exception as cycle_error:
                error_msg = f"Cycle {cycle + 1} failed: {str(cycle_error)}"
                test_results["errors"].append(error_msg)
                test_results["success"] = False

                if console:
                    console.print(f"  ❌ {error_msg}", style="red")

        test_results["total_time"] = time.time() - start_time

        # Print summary
        if console:
            console.print("")
            console.print("📊 Test Results:")
            console.print(
                f"   Cycles completed: {test_results['cycles_completed']}/{cycles}"
            )
            console.print(f"   Total time: {test_results['total_time']:.1f}s")

            if test_results["errors"]:
                console.print(f"   Errors: {len(test_results['errors'])}")
                for error in test_results["errors"]:
                    console.print(f"     - {error}", style="red")

            if test_results["success"]:
                console.print("   Overall result: ✅ PASS", style="green")
            else:
                console.print("   Overall result: ❌ FAIL", style="red")
        else:
            print("Pen Test Results:")
            print(f"  Cycles: {test_results['cycles_completed']}/{cycles}")
            print(f"  Time: {test_results['total_time']:.1f}s")
            print(f"  Result: {'PASS' if test_results['success'] else 'FAIL'}")

            if test_results["errors"]:
                print("  Errors:")
                for error in test_results["errors"]:
                    print(f"    - {error}")

    except Exception as e:
        error_handler.handle(e)
