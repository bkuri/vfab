from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class JobReporter:
    """Generates comprehensive reports for multi-pen plotting jobs."""

    def __init__(self, job_dir: Path):
        self.job_dir = job_dir
        self.job_id = job_dir.name

    def generate_report(
        self, plan_data: Optional[Dict] = None, plot_results: Optional[Dict] = None
    ) -> str:
        """Generate comprehensive HTML report.

        Args:
            plan_data: Planning data from plan.json
            plot_results: Results from plotting

        Returns:
            HTML report content
        """
        # Load plan data if not provided
        if plan_data is None:
            plan_file = self.job_dir / "plan.json"
            if plan_file.exists():
                plan_data = json.loads(plan_file.read_text())
            else:
                plan_data = {}

        # Load plot results if not provided
        if plot_results is None:
            results_file = self.job_dir / "plot_results.json"
            if results_file.exists():
                plot_results = json.loads(results_file.read_text())
            else:
                plot_results = {}

        # Generate HTML report
        html_content = self._generate_html_report(plan_data, plot_results)

        # Save report
        report_file = self.job_dir / "report.html"
        report_file.write_text(html_content, encoding="utf-8")

        return str(report_file)

    def _generate_html_report(
        self, plan_data: Optional[Dict] = None, plot_results: Optional[Dict] = None
    ) -> str:
        """Generate HTML content for the report."""

        # Extract data
        layers = plan_data.get("layers", []) if plan_data else []
        pen_map = plan_data.get("pen_map", {}) if plan_data else {}
        estimates = plan_data.get("estimates", {}) if plan_data else {}

        # Calculate totals
        total_layers = len(layers)
        total_elements = sum(layer.get("element_count", 0) for layer in layers)

        # Plot results
        layers_plotted = plot_results.get("layers_plotted", []) if plot_results else []
        layers_skipped = plot_results.get("layers_skipped", []) if plot_results else []
        pen_swaps = plot_results.get("pen_swaps", 0) if plot_results else 0

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ploTTY Job Report - {self.job_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}
        .header .job-id {{
            color: #7f8c8d;
            font-size: 1.2em;
            margin-top: 5px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 1.1em;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        .layer-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .layer-table th,
        .layer-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        .layer-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}
        .layer-table tr:hover {{
            background-color: #f8f9fa;
        }}
        .status-success {{
            color: #27ae60;
            font-weight: bold;
        }}
        .status-skipped {{
            color: #f39c12;
            font-weight: bold;
        }}
        .status-failed {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .pen-badge {{
            background: #3498db;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.9em;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
        }}
        .metric-card h4 {{
            margin: 0 0 8px 0;
            color: #2c3e50;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #3498db;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 30px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖊️ ploTTY Job Report</h1>
            <div class="job-id">Job ID: {self.job_id}</div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Layers</h3>
                <div class="value">{total_layers}</div>
            </div>
            <div class="summary-card">
                <h3>Elements</h3>
                <div class="value">{total_elements:,}</div>
            </div>
            <div class="summary-card">
                <h3>Layers Plotted</h3>
                <div class="value">{len(layers_plotted)}</div>
            </div>
            <div class="summary-card">
                <h3>Pen Swaps</h3>
                <div class="value">{pen_swaps}</div>
            </div>
        </div>
        
        {self._generate_estimates_section(estimates) if estimates else ""}
        
        {self._generate_layers_section(layers, layers_plotted, layers_skipped, pen_map) if layers else ""}
        
        {self._generate_plotting_section(plot_results) if plot_results else ""}
        
        <div class="timestamp">
            Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
</body>
</html>
        """
        return html

    def _generate_estimates_section(self, estimates: Dict) -> str:
        """Generate estimates section."""
        pre_time = estimates.get("pre_s", 0)
        post_time = estimates.get("post_s", 0)
        time_saved = estimates.get("time_saved_percent", 0)

        return f"""
        <div class="section">
            <h2>⏱️ Time Estimates</h2>
            <div class="metrics">
                <div class="metric-card">
                    <h4>Pre-optimization</h4>
                    <div class="metric-value">{pre_time:.1f}s</div>
                </div>
                <div class="metric-card">
                    <h4>Post-optimization</h4>
                    <div class="metric-value">{post_time:.1f}s</div>
                </div>
                <div class="metric-card">
                    <h4>Time Saved</h4>
                    <div class="metric-value">{time_saved:.1f}%</div>
                </div>
            </div>
        </div>
        """

    def _generate_layers_section(
        self,
        layers: List[Dict],
        layers_plotted: List[Dict],
        layers_skipped: List[str],
        pen_map: Dict,
    ) -> str:
        """Generate layers section."""

        # Create lookup for plotted layers
        plotted_by_name = {layer["name"]: layer for layer in layers_plotted}

        rows = ""
        for layer in sorted(layers, key=lambda layer_item: layer_item["order_index"]):
            layer_name = layer["name"]
            pen = pen_map.get(layer_name, "Unknown")
            elements = layer.get("element_count", 0)

            # Determine status
            if layer_name in plotted_by_name:
                status = '<span class="status-success">✓ Plotted</span>'
                time_info = f"{plotted_by_name[layer_name]['time']:.1f}s"
                distance_info = f"{plotted_by_name[layer_name]['distance']:.1f}mm"
            elif layer_name in layers_skipped:
                status = '<span class="status-skipped">⏭️ Skipped</span>'
                time_info = "-"
                distance_info = "-"
            else:
                status = '<span class="status-failed">✗ Failed</span>'
                time_info = "-"
                distance_info = "-"

            rows += f"""
                <tr>
                    <td>{layer_name}</td>
                    <td><span class="pen-badge">{pen}</span></td>
                    <td>{elements:,}</td>
                    <td>{time_info}</td>
                    <td>{distance_info}</td>
                    <td>{status}</td>
                </tr>
            """

        return f"""
        <div class="section">
            <h2>📚 Layer Details</h2>
            <table class="layer-table">
                <thead>
                    <tr>
                        <th>Layer Name</th>
                        <th>Pen</th>
                        <th>Elements</th>
                        <th>Time</th>
                        <th>Distance</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        """

    def _generate_plotting_section(self, plot_results: Dict) -> str:
        """Generate plotting results section."""

        total_time = plot_results.get("total_time", 0)
        total_distance = plot_results.get("total_distance", 0)
        pen_swaps = plot_results.get("pen_swaps", 0)
        errors = plot_results.get("errors", [])

        return f"""
        <div class="section">
            <h2>🖊️ Plotting Results</h2>
            <div class="metrics">
                <div class="metric-card">
                    <h4>Total Time</h4>
                    <div class="metric-value">{total_time:.1f}s</div>
                </div>
                <div class="metric-card">
                    <h4>Total Distance</h4>
                    <div class="metric-value">{total_distance:.1f}mm</div>
                </div>
                <div class="metric-card">
                    <h4>Pen Swaps</h4>
                    <div class="metric-value">{pen_swaps}</div>
                </div>
            </div>
            
            {self._generate_errors_section(errors) if errors else ""}
        </div>
        """

    def _generate_errors_section(self, errors: List[str]) -> str:
        """Generate errors section."""

        error_rows = ""
        for error in errors:
            error_rows += f"<li>{error}</li>"

        return f"""
        <div style="margin-top: 20px;">
            <h4 style="color: #e74c3c;">⚠️ Errors</h4>
            <ul style="color: #e74c3c;">
                {error_rows}
            </ul>
        </div>
        """

    def save_plot_results(self, plot_results: Dict) -> None:
        """Save plotting results to JSON file."""
        results_file = self.job_dir / "plot_results.json"
        results_file.write_text(json.dumps(plot_results, indent=2), encoding="utf-8")

    def get_metrics_summary(self) -> Dict:
        """Get a summary of job metrics."""
        plan_file = self.job_dir / "plan.json"
        results_file = self.job_dir / "plot_results.json"

        summary = {
            "job_id": self.job_id,
            "has_plan": plan_file.exists(),
            "has_results": results_file.exists(),
        }

        if plan_file.exists():
            plan_data = json.loads(plan_file.read_text())
            summary.update(
                {
                    "layer_count": plan_data.get("layer_count", 0),
                    "total_elements": sum(
                        layer.get("element_count", 0)
                        for layer in plan_data.get("layers", [])
                    ),
                    "pen_map": plan_data.get("pen_map", {}),
                    "estimates": plan_data.get("estimates", {}),
                }
            )

        if results_file.exists():
            plot_results = json.loads(results_file.read_text())
            summary.update(
                {
                    "plot_success": plot_results.get("success", False),
                    "layers_plotted": len(plot_results.get("layers_plotted", [])),
                    "layers_skipped": len(plot_results.get("layers_skipped", [])),
                    "total_time": plot_results.get("total_time", 0),
                    "total_distance": plot_results.get("total_distance", 0),
                    "pen_swaps": plot_results.get("pen_swaps", 0),
                    "error_count": len(plot_results.get("errors", [])),
                }
            )

        return summary
