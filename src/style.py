"""One visual system for every figure in the paper."""

from __future__ import annotations
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.text import Text
from .paths import FIGURES

SERIES = [
    "#2a78d6",
    "#eb6834",
    "#1baf7a",
    "#eda100",
    "#e87ba4",
    "#008300",
    "#4a3aa7",
    "#e34948",
]
SEQUENTIAL = [
    "#cde2fb",
    "#9ec5f4",
    "#6da7ec",
    "#3987e5",
    "#256abf",
    "#184f95",
    "#0d366b",
]
DIVERGING_NEG, DIVERGING_MID, DIVERGING_POS = ("#2a78d6", "#f0efec", "#e34948")
COLORS = {
    "ink": "#0b0b0b",
    "ink2": "#52514e",
    "muted": "#898781",
    "grid": "#e1e0d9",
    "axis": "#c3c2b7",
    "surface": "#ffffff",
    "context": "#c3c2b7",
}
ENTITY_COLORS = {
    "commercial": SERIES[0],
    "open_source": SERIES[1],
    "prepackaged": SERIES[0],
    "custom": SERIES[2],
    "own_account": SERIES[1],
    "Python": SERIES[0],
    "JavaScript": SERIES[3],
    "TypeScript": SERIES[6],
    "Rust": SERIES[1],
    "Go": SERIES[2],
    "Java": SERIES[7],
    "C++": SERIES[4],
    "C#": SERIES[5],
}
WIDTH_FULL = (7.0, 3.6)
WIDTH_HALF = (3.4, 2.6)
WIDTH_TALL = (7.0, 5.2)
PAPER_WIDTH_IN = 6.5
SINGLE_PANEL_WIDTH_FRACTIONS = {"f09_aider_cost_frontier": 0.75}
MULTIPANEL_HEIGHTS = {
    "f03_pkg_new_monthly": 5.2,
    "f02_ig_activity": 3.6,
    "f05_ai_commit_share": 3.8,
    "f04_alternative_rate": 5.7,
    "f10_homebrew_installs": 5.5,
    "f17_capability_projection": 4.5,
    "f18_freelance_platform_shares": 3.7,
    "f19_preagent_backtest": 3.65,
}
SINGLE_PANEL_FONTS = {
    "axis": 10.5,
    "tick": 9.5,
    "annotation": 9.0,
    "legend": 9.0,
    "source": 7.5,
}


def apply() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 110,
            "savefig.dpi": 300,
            "figure.facecolor": COLORS["surface"],
            "axes.facecolor": COLORS["surface"],
            "font.family": "serif",
            "font.serif": ["Times New Roman", "TeX Gyre Termes", "DejaVu Serif"],
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.labelsize": 9,
            "axes.labelcolor": COLORS["ink2"],
            "axes.edgecolor": COLORS["axis"],
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "axes.axisbelow": True,
            "axes.prop_cycle": mpl.cycler(color=SERIES),
            "grid.color": COLORS["grid"],
            "grid.linewidth": 0.6,
            "grid.linestyle": "-",
            "xtick.color": COLORS["muted"],
            "ytick.color": COLORS["muted"],
            "xtick.labelcolor": COLORS["ink2"],
            "ytick.labelcolor": COLORS["ink2"],
            "xtick.major.size": 3,
            "ytick.major.size": 0,
            "lines.linewidth": 2.0,
            "lines.markersize": 5,
            "legend.frameon": False,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def source_note(fig, text: str) -> None:
    """Source attribution below the figure."""
    text = _without_retrieval_note(text)
    note = fig.text(
        0.01, 0.005, text, fontsize=6.5, color=COLORS["muted"], ha="left", va="bottom"
    )
    note.set_gid("source-note")
    note._source_text = text


def _wrap_source(note: Text, fig, available_inches: float | None = None) -> None:
    """Wrap provenance using measured glyph widths at the final print size."""
    renderer = fig.canvas.get_renderer()
    available = (
        available_inches if available_inches is not None else fig.get_figwidth() * 0.97
    ) * fig.dpi
    properties = note.get_fontproperties()
    lines = []
    for paragraph in getattr(note, "_source_text", note.get_text()).splitlines():
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            width = renderer.get_text_width_height_descent(
                candidate, properties, False
            )[0]
            if current and width > available:
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
    note.set_text("\n".join(lines))


def align_source_notes(fig, name: str, fixed_canvas: bool) -> None:
    """Align every note with the artwork, including labels, in main and appendix plots."""
    notes = [text for text in fig.texts if text.get_gid() == "source-note"]
    if not notes:
        return
    for note in notes:
        note.set_in_layout(False)
        note.set_ha("left")
        note.set_va("bottom")
    fig.canvas.draw()
    art = fig.get_tightbbox(fig.canvas.get_renderer())
    width, height = fig.get_size_inches()
    final_width = PAPER_WIDTH_IN * SINGLE_PANEL_WIDTH_FRACTIONS.get(name, 1.0)
    scale = 1.0 if fixed_canvas else final_width / (art.width + 0.2)
    gap = 8 / 72 / scale
    for note in notes:
        note.set_fontsize(SINGLE_PANEL_FONTS["source"] / scale)
        _wrap_source(note, fig, art.width)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    note_heights = [note.get_window_extent(renderer).height / fig.dpi for note in notes]
    note_height = sum(note_heights) + max(0, len(notes) - 1) * 2 / 72 / scale
    if fixed_canvas:
        bottom = 6 / 72
        target = bottom + note_height + gap
        axes = [ax for ax in fig.axes if ax.get_visible()]
        for _ in range(5):
            art = fig.get_tightbbox(fig.canvas.get_renderer())
            if abs(target - art.y0) < 0.004:
                break
            top = max((ax.get_position().y1 for ax in axes)) * height
            factor = (top - target) / (top - art.y0)
            if factor <= 0:
                raise ValueError(f"Source note leaves no chart area: {name}")
            for ax in axes:
                box = ax.get_position()
                y0 = top + (box.y0 * height - top) * factor
                ax.set_position([box.x0, y0 / height, box.width, box.height * factor])
            fig.canvas.draw()
        art = fig.get_tightbbox(fig.canvas.get_renderer())
    else:
        bottom = art.y0 - gap - note_height
    for note, line_height in zip(notes, note_heights):
        note.set_position((art.x0 / width, bottom / height))
        note.set_in_layout(not fixed_canvas)
        bottom += line_height + 2 / 72 / scale
    fig.canvas.draw()


def has_full_width_panels(fig) -> bool:
    """Single axes and vertically stacked panels need the same print-size type."""
    axes = [ax for ax in fig.axes if ax.get_visible()]
    if len(axes) == 1:
        return True
    return bool(axes) and all(
        (
            ax.get_subplotspec() is not None
            and ax.get_subplotspec().get_gridspec().ncols == 1
            for ax in axes
        )
    )


def format_single_panel(fig, name: str) -> None:
    """Apply common print sizes to single axes or full-width stacked panels."""
    if getattr(fig, "_paper_typography_applied", False):
        return
    width = PAPER_WIDTH_IN * SINGLE_PANEL_WIDTH_FRACTIONS.get(name, 1.0)
    old_width, old_height = fig.get_size_inches()
    height = MULTIPANEL_HEIGHTS.get(name, max(3.0, old_height * width / old_width))
    fig.set_size_inches(width, height, forward=True)
    axes = [ax for ax in fig.axes if ax.get_visible()]
    for ax in axes:
        for text in ax.findobj(match=Text):
            text.set_fontsize(SINGLE_PANEL_FONTS["annotation"])
        ax.xaxis.label.set_fontsize(SINGLE_PANEL_FONTS["axis"])
        ax.yaxis.label.set_fontsize(SINGLE_PANEL_FONTS["axis"])
        ax.tick_params(axis="both", which="both", labelsize=SINGLE_PANEL_FONTS["tick"])
        ax.xaxis.get_offset_text().set_fontsize(SINGLE_PANEL_FONTS["tick"])
        ax.yaxis.get_offset_text().set_fontsize(SINGLE_PANEL_FONTS["tick"])
        for title in (ax.title, ax._left_title, ax._right_title):
            title.set_fontsize(SINGLE_PANEL_FONTS["axis"])
        if ax.get_legend() is not None:
            for text in ax.get_legend().get_texts():
                text.set_fontsize(SINGLE_PANEL_FONTS["legend"])
    notes = [text for text in fig.texts if text.get_gid() == "source-note"]
    keys = [text for text in fig.texts if text.get_gid() != "source-note"]
    for text in keys:
        text.set_fontsize(SINGLE_PANEL_FONTS["legend"])
    for legend in fig.legends:
        for text in legend.get_texts():
            text.set_fontsize(SINGLE_PANEL_FONTS["legend"])
    for note in notes:
        note.set_fontsize(SINGLE_PANEL_FONTS["source"])
        note.set_position((0.015, 0.018))
        note.set_in_layout(False)
    fig.canvas.draw()
    for note in notes:
        _wrap_source(note, fig)
    fig.canvas.draw()
    note_height = max(
        (note.get_window_extent().height / fig.dpi for note in notes), default=0
    )
    bottom = (note_height + 0.15) / height if notes else 0.02
    right = min((text.get_position()[0] for text in keys), default=1.015) - 0.03
    top = 0.9 if fig.legends else 0.99
    fig.tight_layout(
        rect=(0.015, bottom, min(right, 0.985), top), pad=0.8, h_pad=2.5, w_pad=2.0
    )
    if name in MULTIPANEL_HEIGHTS:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        for ax in axes:
            for title in (ax.title, ax._left_title, ax._right_title):
                lines = []
                for paragraph in title.get_text().splitlines():
                    line = ""
                    for word in paragraph.split():
                        candidate = f"{line} {word}".strip()
                        measured = renderer.get_text_width_height_descent(
                            candidate, title.get_fontproperties(), False
                        )[0]
                        if line and measured > ax.get_window_extent(renderer).width:
                            lines.append(line)
                            line = word
                        else:
                            line = candidate
                    lines.append(line)
                title.set_text("\n".join(lines))
        fig.tight_layout(
            rect=(0.015, bottom, min(right, 0.985), top), pad=0.8, h_pad=2.5, w_pad=2.0
        )
    fig._paper_typography_applied = True


def label_end(ax, x, y, text: str, color: str, dx: float = 4, dy: float = 0) -> None:
    """Direct label at a line's end point (use instead of a legend for <= 4 lines)."""
    ax.annotate(
        text,
        xy=(x, y),
        xytext=(dx, dy),
        textcoords="offset points",
        color=COLORS["ink2"],
        fontsize=8,
        va="center",
        ha="left",
    )
    ax.plot(
        [x],
        [y],
        "o",
        color=color,
        markersize=4,
        markeredgecolor=COLORS["surface"],
        markeredgewidth=1,
    )


def save(fig, name: str) -> None:
    """Save PDF and PNG figures to the output directory."""
    if fig._suptitle is not None:
        fig._suptitle.remove()
        fig._suptitle = None
    visible_axes = [ax for ax in fig.axes if ax.get_visible()]
    if len(visible_axes) == 1:
        for position in ("left", "center", "right"):
            visible_axes[0].set_title("", loc=position)
    consistent = has_full_width_panels(fig) or name in MULTIPANEL_HEIGHTS
    if consistent:
        format_single_panel(fig, name)
    fixed_canvas = consistent or name == "f02_ig_languages"
    align_source_notes(fig, name, fixed_canvas=fixed_canvas)
    bounds = None if fixed_canvas else "tight"
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches=bounds)
    fig.savefig(FIGURES / f"{name}.png", bbox_inches=bounds)


def _without_retrieval_note(text):
    import re

    text = re.sub(
        r"(?:METR|Epoch)\s+(?:retrieved|last accessed)\s*[^\n]*?(?:\d{4}-\d{2}-\d{2}|[.;](?=\s|$))\.?",
        "",
        text,
        flags=re.I,
    )
    return re.sub(
        r"(?:Data )?(?:[Rr]etrieved|[Ll]ast accessed)\s*[^\n]*?(?:\d{4}-\d{2}-\d{2}|[.;](?=\s|$))\.?",
        "",
        text,
    ).strip()
