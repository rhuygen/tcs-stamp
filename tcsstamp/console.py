try:
    from rich.console import Console
    from rich.table import Table


    def print_table(data):
        """
        This convenience function prints the last sampled housekeeping parameters in a table in your
        console. This function is for use in a REPL or Jupyter Notebook.

        Note that when no task is running most of the housekeeping parameters are not sampled and the
        values will be out-of-date. To make sure you have up-to-date values, run the task.
        """
        table = Table(title="All Telemetry")

        table.add_column("Date Time", justify="center", style="cyan", no_wrap=True)
        table.add_column("Name", justify="left", style="magenta")
        table.add_column("Value", justify="right", style="green")

        if isinstance(data, dict):
            data = data.values()

        for date, name, value in data:
            table.add_row(date, name, value)

        console = Console()
        console.print(table)

except ModuleNotFoundError:
    def print_table(data):
        print(f"{data=}")
