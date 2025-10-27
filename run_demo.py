from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, List, Tuple

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

from minic import parse_ll1, ParseError
from minic.lexer import LexerError

app = typer.Typer(no_args_is_help=True)
console = Console()

DEFAULT_DIR = "test_to_parse"
DEFAULT_EXTS = {".c", ".txt"}


def classify(text: str) -> Tuple[bool, str]:
    """Devuelve (ok, msg). ok=True si el parser acepta; msg con detalle."""
    try:
        parse_ll1(text)
        return True, "ACEPTADO"
    except (ParseError, LexerError) as e:
        return False, f"RECHAZADO: {e}"


def find_files(folder: Path, exts: Iterable[str]) -> List[Path]:
    exts_norm = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in exts}
    return sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in exts_norm
    )


@app.command(help="Recorre una carpeta y reporta si cada archivo es ACEPTADO o RECHAZADO por el parser LL(1).")
def run(
    carpeta: Path = typer.Argument(
        Path(DEFAULT_DIR),
        exists=False,
        dir_okay=True,
        file_okay=False,
        readable=True,
        help="Carpeta con archivos a analizar."
    ),
    ext: List[str] = typer.Option(
        list(DEFAULT_EXTS), "--ext", "-e",
        help="Extensiones a incluir (puedes repetir la opción). Ej: -e .c -e .txt"
    ),
):
    if not carpeta.exists() or not carpeta.is_dir():
        console.print(f"[red]✖ Carpeta no encontrada:[/red] {carpeta}")
        raise typer.Exit(code=2)

    files = find_files(carpeta, ext)
    if not files:
        console.print(Panel.fit(f"[yellow]No hay archivos con extensiones {sorted({e if e.startswith('.') else '.'+e for e in ext})} en:[/yellow]\n[bold]{carpeta}[/bold]"))
        raise typer.Exit(code=0)

    console.print(Panel.fit(
        f"[bold]Analizando {len(files)} archivo(s)[/bold] en [cyan]{carpeta}[/cyan]\n"
        f"[dim]Extensiones: {', '.join(sorted({e if e.startswith('.') else '.'+e for e in ext}))}[/dim]",
        title="LL(1) Runner", border_style="blue"
    ))

    table = Table(title="Resultados", show_lines=False)
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Archivo", style="white")
    table.add_column("Estado", justify="center", style="bold")
    table.add_column("Detalle", style="dim")

    ok = 0
    for idx, path in enumerate(track(files, description="Procesando...", console=console), start=1):
        text = path.read_text(encoding="utf-8", errors="ignore")
        accepted, msg = classify(text)
        status_text = "[green]ACEPTADO[/green]" if accepted else "[red]RECHAZADO[/red]"
        if accepted:
            ok += 1
            detail = "-"
        else:
            # mostrar solo el inicio del error para no alargar
            detail = msg.replace("RECHAZADO: ", "")
        table.add_row(str(idx), str(path), status_text, detail)

    console.print()
    console.print(table)

    total = len(files)
    rej = total - ok
    summary = f"[bold green]Aceptados:[/bold green] {ok}/{total}   [bold red]Rechazados:[/bold red] {rej}/{total}"
    console.print(Panel.fit(summary, title="Resumen", border_style="magenta"))

    # Código de salida 0 (no fallar el proceso). Si quisieras fallar si hay rechazados, usa:
    # raise typer.Exit(code=1 if rej > 0 else 0)
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
