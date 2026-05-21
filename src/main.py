from Horus import site_scanner
import json
import asyncio
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
[/bold dark_yellow]
"""

if __name__ == "__main__":
    console = Console()
    console.print(BANNER)
    console.print("[bold blue]-[/bold blue]" * 65)
    dir = Path(__file__).parent
    file = dir / "sites.json"
    with open(file, "r") as file:
        sites = json.load(file)
    username = console.input("[?] - Enter the username you want to search : ")
    if username.strip():
        results = asyncio.run(site_scanner(username, sites))
        print("\n--- Scan Results ---\n")
        for res in results:
            if res is None:
                continue
            if res.get("Found"):
                console.print(f"[bold dark_green][+] - Username found in {res['site']} : {res['url']}[/bold dark_green]")
            elif "error" in res:
                console.print(f"[bold purple][!] - Error in {res['site']} : {res['error']}[/bold purple]")
            else:
                console.print(f"[bold yellow][-] - Error: username not found in {res['site']}[/bold yellow]")
    else:
        console.print(f"[bold red][X] - Please enter a valid username[/bold red]")