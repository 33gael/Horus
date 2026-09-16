from Horus import site_scanner
import json
import asyncio
import re
import sys
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.style import Style
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn
from urllib.parse import urlsplit

BANNER = r"""
[bold dark_yellow]
                                    ....:OkdddxxxxO0k:'......         
                           . ..,'cdldddxK00000000000KKOkkOkxxx,,'.    
                   . ...,:.':,odx000000000000KKKKKKKKKKKKKKKKKOOxxll. 
             ...cl'..,.'oxxO0KKKKKKK0xdxxxdddxxxxxkOOOO0KXXXXXXXXXKOdd
.,xxddooolllc:cx00000KKKKKKKKXlccllxc...... ... . .....,xkxxkkKNNNNNx0
.kOKKKKKKKKKKKKKKKKKK0O0o.'',k.......                    .....:koool:.
.kO000000OOkkkkkx:'':..,:...              ...........               
.':::::,,,,'',::.. ...              ..lccdxdxOOO0OOkkxll,.           
                               ..:dlokOO00000000O00K0000kko..        
                           ...kccdK00KddddkKK0000000K0kxO00xd'.       
 .,,,''''''''.......'.....c,clKK0Oxlc,.OxK0Oxdddddxk00Okxd0KKko'.     
.kOKK00Okkxxxdddoooolllld0KKOxoc:,... .loKKKKKKKKKKKKKko,.:xOKKxo,.   
.kOXXXXXXXXXXXXXXXXXXXXXXXXOc:::l.... .:'oXXXXXXXXXXXO:,'...:dOKkd:.  
.,kxxxddolccc::,'''.....''',:xXKKkollx,.',lXNNNNNNNNOlxxddxxxddOXXkk' 
                           ...o:lxXXNNXOxxxxxxkkkkkO0NNNNXXXNNXKkdo'. 
                                .':clod0KKKKKXXXXXKOkkxolldxo:'.....  
                                  .'oxKWWNKKOxx0XNKd'....             
                                .'ox0NWWWWNkdxkXNNNkxd: .             
                               '0x0NNNWWNxd:.lxKXXXXX0l..             
                           ..'xxONNNNN0xo.. .cx0XXXX0xc.              
   .,,,,:.                :lokKXXXXKOkd... ..cd0KKK0oc..              
 .oxxkkklcd.           :oldOKXXXKkko'....   .odOKKKdc.                
.kk0ko:ko0:,.       .ccoOKKKKKxxd'.          olkKK0d'..               
.kOkxkdOo0:c. ...c',:KKKKKkdok..             c:k000k..                
.kk0koxkl:d'c,':cO0000kxolc'..               ,,k000O'..               
.'xxO0kxdddx00000xoo,d,:...                  .:dO00o:...           
...,lddoolllc:,':'.,...                      .,odO0dl.               
      ............ ...                        ..lkkk.                 
[/]
"""

def get_valid_username(console: Console) -> str:
    while True:
        raw_username = console.input("[bold cyan][?] - Enter the username you want to search : [/]")
        clean_username = re.sub(r'[^a-zA-Z0-9_\-.]', '', raw_username)
        if not re.fullmatch(r"[a-zA-Z0-9_][a-zA-Z0-9_.-]{0,99}", clean_username):
            console.print("[bold red][X] - Please enter a valid username (special characters alone are not allowed).[/]")
            continue
        if clean_username != raw_username:
            console.print(f"[bold yellow][!] - Special characters ignored. Searching for : '{clean_username}'...[/]")
        return clean_username

def print_result(console, res):
    if res is None:
        return
    site = str(res.get("site", "Unknown site"))
    status = res.get("status")
    if res.get("Found"):
        line = Text("[+] - Username found in ", style="bold dark_green")
        line.append(f"{site} :", style="bold white")
    elif status == "not_found":
        console.print(Text(f"[-] - Username not found in {site}", style="bold orange3"))
        return
    elif status == "blocked":
        line = Text(f"[!] - Access blocked on {site}: {res.get('error', 'Access denied')}", style="bold purple")
    else:
        line = Text(f"[?] - Unable to verify {site}: {res.get('error', 'Profile could not be verified')}", style="bold purple")
    if res.get("Found"):
        url = res.get("requested_url", res.get("url")) if site in ("Facebook", "LinkedIn") else res.get("url")
        try:
            if isinstance(url, str) and not any(ord(char) < 32 for char in url):
                parsed = urlsplit(url)
                if parsed.scheme in ("https", "http") and parsed.hostname and not parsed.username and not parsed.password:
                    line.append(" ")
                    line.append(url, style=Style(color="cyan", underline=True, link=url))
        except ValueError:
            pass
    console.print(line, soft_wrap=True)


if __name__ == "__main__":
    console = Console()
    try:
        console.print(BANNER, crop=False, overflow="ignore")
        console.print("[bold blue]-[/]" * 75)
        dir = Path(__file__).parent
        file_path = dir / "sites.json"
        with open(file_path, "r") as f:
            sites = json.load(f)
        username = get_valid_username(console)
        with Progress(
            SpinnerColumn(),
            BarColumn(bar_width=32),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("scan", total=len(sites))
            results = asyncio.run(site_scanner(username, sites, lambda: progress.advance(task)))

        for res in results:
            print_result(console, res)
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold red][!] - Scan interrupted by user. Exiting Horus...[/bold red]")
        sys.exit(0)
