from ft_Sherlock import site_scanner
import json
import asyncio
from pathlib import Path
from rich.console import Console

if __name__ == "__main__":
    console = Console()
    dir = Path(__file__).parent
    file = dir / "sites.json"
    with open(file, "r") as file:
        sites = json.load(file)
    username = console.input("[?] - Enter the username you want to search : ")
    if username.strip():
        results = asyncio.run(site_scanner(username, sites))
        print("\n--- Scan Results ---\n")
        for res in results:
            if res.get("Found"):
                console.print(f"[bold dark_green][+] - Username found in {res['site']} : {res['url']}[/bold dark_green]")
            elif "error" in res:
                console.print(f"[bold dark_red][!] - Error in {res['site']} : {res['error']}[/bold dark_red]")
            else:
                console.print(f"[bold dark_orange][-] - Error username not found in {res['site']}[/bold dark_orange]")
    else:
        console.print(f"[bold red][X] - Please enter a valid username[/bold red]")