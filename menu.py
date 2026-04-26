#!/usr/bin/env python3
"""
Interfaz Interactiva (TUI) para el Monitor de Convocatorias Europeas
Usa Rich y Questionary para una experiencia de usuario guiada.
"""

import sys
import os
import time
from datetime import datetime

# Intentar importar librerías de UI, si fallan avisar de la instalación
try:
    import questionary
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
except ImportError:
    print("❌ Faltan dependencias de UI. Por favor, ejecuta:")
    print("pip install rich questionary")
    sys.exit(1)

from eu_api_monitor import EUAPIMonitor
from notification_service import NotificationService
from config import MUNICIPALITY_CONFIG, DATA_DIR, SPAIN_GEOGRAPHY

console = Console()

def show_welcome():
    """Muestra el banner de bienvenida"""
    console.clear()
    welcome_text = f"""
    [bold cyan]🚀 MONITOR DE CONVOCATORIAS EUROPEAS[/bold cyan]
    [bold white]Municipio:[/bold white] {MUNICIPALITY_CONFIG['name']} ({MUNICIPALITY_CONFIG['population']} hab.)
    [bold white]Estado:[/bold white] [green]Activo y listo[/green]
    """
    console.print(Panel(welcome_text, title="AytoRural Monitor", border_style="cyan"))

def run_search_ui():
    """Ejecuta una búsqueda geográfica interactiva"""
    
    scope = questionary.select(
        "¿Qué ámbito quieres consultar?",
        choices=[
            "🇪🇸 Nacional (Toda España)",
            "🗺️ Regional (Comunidad Autónoma)",
            "📍 Provincial",
            "🔍 Búsqueda por palabra clave libre",
            "⬅️ Volver"
        ]
    ).ask()

    if scope == "⬅️ Volver":
        return

    search_term = ""
    if scope == "🇪🇸 Nacional (Toda España)":
        search_term = "España rural"
    
    elif scope == "🗺️ Regional (Comunidad Autónoma)":
        ccaa = questionary.select(
            "Selecciona la Comunidad Autónoma:",
            choices=sorted(list(SPAIN_GEOGRAPHY.keys()))
        ).ask()
        search_term = f"{ccaa} rural"
        
    elif scope == "📍 Provincial":
        ccaa = questionary.select(
            "Primero, selecciona la Comunidad Autónoma:",
            choices=sorted(list(SPAIN_GEOGRAPHY.keys()))
        ).ask()
        provincia = questionary.select(
            f"Ahora, selecciona la provincia de {ccaa}:",
            choices=sorted(SPAIN_GEOGRAPHY[ccaa])
        ).ask()
        search_term = f"{provincia} rural"
        
    elif scope == "🔍 Búsqueda por palabra clave libre":
        search_term = questionary.text("Escribe el término de búsqueda:").ask()

    if not search_term:
        return

    monitor = EUAPIMonitor()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description=f"Consultando API para '{search_term}'...", total=None)
        results = monitor.search_opportunities(search_term)
        
        progress.update(task, description="Filtrando convocatorias relevantes...")
        new_calls = monitor.process_search_results(results)

    if not new_calls:
        rprint(f"\n[yellow]ℹ️ No se han encontrado nuevas convocatorias para '{search_term}' en este momento.[/yellow]")
    else:
        rprint(f"\n[bold green]✨ ¡Se han encontrado {len(new_calls)} oportunidades para '{search_term}'![/bold green]")
        
        table = Table(title=f"Resultados para {search_term}")
        table.add_column("Título", style="cyan", no_wrap=False)
        table.add_column("Presupuesto", style="green")
        table.add_column("Plazo", style="magenta")

        for call in new_calls:
            table.add_row(
                call['title'][:70] + "...",
                call['budget'],
                call['deadline']
            )
        
        console.print(table)
        
        if questionary.confirm("¿Quieres enviar estas notificaciones al Alcalde?").ask():
            with Progress(SpinnerColumn(), TextColumn("Enviando alertas..."), transient=True) as p:
                p.add_task("notify")
                for call in new_calls:
                    monitor.notification_service.send_notifications(call)
                rprint("[green]✅ Notificaciones enviadas.[/green]")

    questionary.press_any_key_to_continue().ask()

def show_stats_ui():
    """Muestra estadísticas en una tabla bonita"""
    monitor = EUAPIMonitor()
    stats = monitor.get_statistics()
    
    console.print("\n[bold cyan]📊 ESTADÍSTICAS DEL MONITOR[/bold cyan]")
    
    table = Table(show_header=False, box=None)
    table.add_row("Municipio", f"[bold]{stats['municipality']}[/bold]")
    table.add_row("Población", f"{stats['population']} habitantes")
    table.add_row("Comunidad", stats['autonomous_community'])
    table.add_row("Total procesadas", f"[green]{stats['total_processed']}[/green]")
    table.add_row("Último chequeo", stats['last_check'][:19].replace("T", " "))
    
    console.print(Panel(table, border_style="blue"))
    
    if monitor.processed_calls:
        rprint("\n[bold]Últimas convocatorias registradas:[/bold]")
        for i, (hash_id, call) in enumerate(list(monitor.processed_calls.items())[-3:], 1):
            rprint(f"  {i}. [cyan]{call['title'][:60]}...[/cyan] ([dim]{call['processed_at'][:10]}[/dim])")
    
    questionary.press_any_key_to_continue().ask()

def test_notifications_ui():
    """Prueba de notificaciones interactiva"""
    method = questionary.select(
        "¿Qué canal quieres probar?",
        choices=[
            "Telegram",
            "WhatsApp",
            "Ambos",
            "Volver"
        ]
    ).ask()
    
    if method == "Volver":
        return

    method_map = {"Telegram": "telegram", "WhatsApp": "whatsapp", "Ambos": "both"}
    service = NotificationService()
    
    with console.status("[bold green]Enviando mensaje de prueba...") as status:
        success = service.send_test_message(method_map[method])
        time.sleep(1)
        
    if success:
        rprint("[bold green]✅ ¡Mensaje enviado con éxito![/bold green]")
    else:
        rprint("[bold red]❌ Error al enviar el mensaje.[/bold red]")
        rprint("[dim]Asegúrate de que el archivo .env tiene las claves correctas.[/dim]")
    
    questionary.press_any_key_to_continue().ask()

def main_menu():
    """Bucle principal del menú"""
    while True:
        show_welcome()
        
        choice = questionary.select(
            "Selecciona una acción:",
            choices=[
                "🔍 Buscar nuevas convocatorias",
                "📊 Ver estadísticas y estado",
                "📤 Probar notificaciones",
                "⚙️  Configurar municipio (Próximamente)",
                "🧹 Limpiar historial",
                "❌ Salir"
            ]
        ).ask()

        if choice == "🔍 Buscar nuevas convocatorias":
            run_search_ui()
        elif choice == "📊 Ver estadísticas y estado":
            show_stats_ui()
        elif choice == "📤 Probar notificaciones":
            test_notifications_ui()
        elif choice == "🧹 Limpiar historial":
            if questionary.confirm("¿Seguro que quieres borrar todo el historial?").ask():
                import os
                processed_file = DATA_DIR / "processed_calls.json"
                if processed_file.exists():
                    os.remove(processed_file)
                    rprint("[green]✅ Historial borrado.[/green]")
                else:
                    rprint("[yellow]No hay historial que borrar.[/yellow]")
                time.sleep(1)
        elif choice == "❌ Salir":
            rprint("[cyan]👋 ¡Hasta pronto! Sigue cuidando de Uclés.[/cyan]")
            break

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        rprint("\n[cyan]👋 Salida forzada por el usuario.[/cyan]")
        sys.exit(0)
