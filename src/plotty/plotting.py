from __future__ import annotations
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable

try:
    from .axidraw_integration import create_manager, is_axidraw_available
except ImportError:
    create_manager = None

    def is_axidraw_available():
        return False


from .multipen import detect_svg_layers, parse_axidraw_layer_control


class PenSwapPrompt:
    """Handles pen swap prompts during multi-pen plotting."""

    def __init__(self, interactive: bool = True):
        self.interactive = interactive
        self.current_pen: Optional[str] = None

    def prompt_pen_swap(
        self, from_pen: Optional[str], to_pen: str, layer_name: str
    ) -> bool:
        """Prompt user to swap pens.

        Args:
            from_pen: Current pen name (None if first layer)
            to_pen: Target pen name
            layer_name: Name of the layer to plot

        Returns:
            True if user confirms ready, False otherwise
        """
        if from_pen == to_pen:
            return True  # No swap needed

        if from_pen is None:
            message = f"Ready to plot layer '{layer_name}' with {to_pen}"
        else:
            message = f"Swap pen from {from_pen} to {to_pen} for layer '{layer_name}'"

        print(f"\n🖊️  {message}")
        print("Actions available:")
        print("  - Press Enter to continue")
        print("  - Type 'skip' to skip this layer")
        print("  - Type 'abort' to cancel plotting")

        if not self.interactive:
            print("Auto-continuing (non-interactive mode)")
            self.current_pen = to_pen
            return True

        while True:
            response = input("> ").strip().lower()

            if response == "" or response == "continue":
                self.current_pen = to_pen
                print(f"✓ Continuing with {to_pen}")
                return True
            elif response == "skip":
                print(f"⏭️  Skipping layer '{layer_name}'")
                return False
            elif response == "abort":
                print("🛑 Plotting aborted by user")
                raise KeyboardInterrupt("Plotting aborted")
            else:
                print("Invalid option. Try: continue, skip, or abort")


class MultiPenPlotter:
    """Handles multi-pen plotting with pen swap management."""

    def __init__(
        self, port: Optional[str] = None, model: int = 1, interactive: bool = True
    ):
        if not is_axidraw_available():
            raise ImportError(
                "AxiDraw support not available. Install with: uv pip install -e '.[axidraw]'"
            )
        self.manager = create_manager(port=port, model=model)
        self.prompt = PenSwapPrompt(interactive)
        self.interactive = interactive

    def plot_multipen_job(
        self,
        job_dir: Path,
        layers: List[Dict],
        pen_map: Dict[str, str],
        progress_callback: Optional[Callable] = None,
    ) -> Dict:
        """Plot a multi-pen job with pen swap prompts.

        Args:
            job_dir: Job directory path
            layers: List of layer information from planning
            pen_map: Layer name to pen mapping
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with plotting results
        """
        results = {
            "success": True,
            "layers_plotted": [],
            "layers_skipped": [],
            "total_time": 0,
            "total_distance": 0,
            "pen_swaps": 0,
            "errors": [],
        }

        start_time = time.time()
        current_pen = None

        # Sort layers by order_index
        sorted_layers = sorted(layers, key=lambda layer: layer["order_index"])

        for i, layer in enumerate(sorted_layers):
            layer_name = layer["name"]
            layer_svg = Path(layer["svg"])
            target_pen = pen_map.get(layer_name, "0.3mm black")

            try:
                # Check if layer file exists
                if not layer_svg.exists():
                    results["errors"].append(f"Layer file not found: {layer_svg}")
                    continue

                # Prompt for pen swap if needed
                if current_pen != target_pen:
                    if self.prompt.prompt_pen_swap(current_pen, target_pen, layer_name):
                        if current_pen is not None:
                            results["pen_swaps"] += 1
                        current_pen = target_pen
                    else:
                        # User skipped this layer
                        results["layers_skipped"].append(layer_name)
                        continue

                # Plot the layer
                print(f"\n📐 Plotting layer {i + 1}/{len(sorted_layers)}: {layer_name}")
                print(f"   Pen: {target_pen}")
                print(f"   Elements: {layer.get('element_count', 'unknown')}")

                # Get pen-specific settings if available
                pen_info = layer.get("pen_info", {})
                plot_options = {}

                if pen_info.get("speed_cap"):
                    plot_options["speed_pendown"] = pen_info["speed_cap"]

                # Plot the layer
                plot_result = self.manager.plot_file(layer_svg, **plot_options)

                if plot_result["success"]:
                    layer_result = {
                        "name": layer_name,
                        "pen": target_pen,
                        "time": plot_result["time_elapsed"],
                        "distance": plot_result["distance_pendown"],
                        "elements": layer.get("element_count", 0),
                    }
                    results["layers_plotted"].append(layer_result)
                    results["total_time"] += plot_result["time_elapsed"]
                    results["total_distance"] += plot_result["distance_pendown"]

                    print(f"   ✓ Completed in {plot_result['time_elapsed']:.1f}s")
                    print(f"   📏 Distance: {plot_result['distance_pendown']:.1f}mm")

                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(i + 1, len(sorted_layers), layer_result)
                else:
                    error_msg = f"Failed to plot layer {layer_name}: {plot_result.get('error', 'Unknown error')}"
                    results["errors"].append(error_msg)
                    print(f"   ✗ {error_msg}")

            except KeyboardInterrupt:
                results["success"] = False
                results["errors"].append("Plotting interrupted by user")
                break
            except Exception as e:
                error_msg = f"Error plotting layer {layer_name}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"   ✗ {error_msg}")

        results["total_time"] = time.time() - start_time

        # Print summary
        print("\n📊 Plotting Summary:")
        print(f"   Layers plotted: {len(results['layers_plotted'])}")
        print(f"   Layers skipped: {len(results['layers_skipped'])}")
        print(f"   Pen swaps: {results['pen_swaps']}")
        print(f"   Total time: {results['total_time']:.1f}s")
        print(f"   Total distance: {results['total_distance']:.1f}mm")

        if results["errors"]:
            print(f"   Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"     - {error}")

        return results

    def plot_with_axidraw_layers(
        self, multipen_svg: Path, progress_callback: Optional[Callable] = None
    ) -> Dict:
        """Plot using AxiDraw's native layer control.

        Args:
            multipen_svg: SVG file with AxiDraw layer control syntax
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with plotting results
        """
        print("\n🖊️  Plotting with AxiDraw native layer control")
        print(f"   File: {multipen_svg}")

        # Parse layers from the SVG to show what will be plotted

        layers = detect_svg_layers(multipen_svg)

        print(f"   Detected {len(layers)} layers:")
        for layer in layers:
            control = parse_axidraw_layer_control(layer.name)
            pen_info = f" (speed: {control.speed})" if control.speed else ""
            pause_info = " [PAUSE]" if control.force_pause else ""
            delay_info = f" (delay: {control.delay_ms}ms)" if control.delay_ms else ""
            print(f"     - {layer.name}{pen_info}{pause_info}{delay_info}")

        # Enable AxiDraw layer mode for native layer control
        # This tells AxiDraw to parse layer names for control codes
        plot_options = {
            "layer_mode": True,  # Enable native layer control
            "layers": "all",  # Plot all layers (respecting control codes)
        }

        # Plot with AxiDraw (it will handle layer control automatically)
        result = self.manager.plot_file(multipen_svg, **plot_options)

        if result["success"]:
            print(f"   ✓ Completed in {result['time_elapsed']:.1f}s")
            print(f"   📏 Total distance: {result['distance_pendown']:.1f}mm")
            print("   🎯 Used AxiDraw native layer control")
        else:
            print(f"   ✗ Failed: {result.get('error', 'Unknown error')}")

        return result
