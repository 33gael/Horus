from Horus import site_scanner
import json
import asyncio
import re
import sys
from pathlib import Path
from rich.console import Console

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
        if not clean_username:
            console.print("[bold red][X] - Please enter a valid username (special characters alone are not allowed).[/]")
            continue
        if clean_username != raw_username:
            console.print(f"[bold yellow][!] - Special characters ignored. Searching for : '{clean_username}'...[/]")
        return clean_username

if __name__ == "__main__":
    console = Console()
    try:
        console.print(BANNER, crop=False, overflow="ignore")
        console.print("[bold blue]-[/]" * 65)
        dir = Path(__file__).parent
        file_path = dir / "sites.json"
        with open(file_path, "r") as f:
            sites = json.load(f)
        username = get_valid_username(console)
        results = asyncio.run(site_scanner(username, sites))

        for res in results:
            if res is None:
                continue
            if res.get("Found"):
                console.print(f"[bold dark_green][+] - Username found in [/][bold white]{res['site']} :[/] {res['url']}")
            elif "error" in res:
                console.print(f"[bold purple][!] - Error in {res['site']} : {res['error']}[/bold purple]")
            else:
                console.print(f"[bold orange3][-] - Error: username not found in [/][bold white]{res['site']}[/]")
    except KeyboardInterrupt:
        console.print("\n[bold red][!] - Scan interrupted by user. Exiting Horus...[/bold red]")
        sys.exit(0)
