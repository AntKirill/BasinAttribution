import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from palettable.colorbrewer.diverging import RdYlBu_11 as colorblind_safe_cmap


def parse_points(file_name):
    _X = np.genfromtxt(file_name, delimiter=",")
    if _X.ndim == 1:
        _X = np.array([_X])
    X = _X[:, 1:]
    return [x for x in X]


def good_plt_config():
    plt.style.use("default")
    with open("latex-preambula.tex", "r") as f:
        latex_preambula = f.read()
    plt.rcParams["text.usetex"] = True
    plt.rc("text.latex", preamble=latex_preambula)
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["ps.fonttype"] = 42
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.linestyle"] = (0, (5, 5))
    plt.rcParams["grid.linewidth"] = 0.5
    mpl.rcParams["font.size"] = 20
    plt.rcParams["xtick.labelsize"] = 20
    plt.rcParams["ytick.labelsize"] = 20


def default_plt_config():
    plt.style.use("default")


def compose_points(f, x, y):
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    for i in range(len(X)):
        for j in range(len(X)):
            Z[i][j] = f(np.array([X[i][j], Y[i][j]]))
    return X, Y, Z


def compute_zax_min_max(zax_min, zax_max, zfactor=1.0, inversion=False):
    h = zax_max - zax_min
    shift = 2 * h * zfactor
    if inversion:
        return zax_max + shift, zax_min
    return zax_min - shift, zax_max


def rastrigin(x):
    N = len(x)
    # c = 2*math.pi
    c = 1.5
    return 10 * N + sum(x[i] ** 2 - 10 * np.cos(c * x[i]) for i in range(N))


def sphere(x):
    return sum((xi - 1) ** 2 for xi in x)


def plot_3D_surface(
    x1_lims,
    x2_lims,
    f,
    X_data,
    discretization=50,
    is_colorbar=False,
    is_axis_names=False,
    is_white_facecolor=False,
    is_scatter_search_space=True,
    is_scatter_objective_space=False,
    zfactor=1.0,
    is_inverse=False,
    is_remove_extra_zlables=False,
    zlabelpad=10,
    is_connect_search_obj=False,
):
    x1 = np.linspace(*x1_lims, discretization)
    x2 = np.linspace(*x2_lims, discretization)
    X1, X2, Z = compose_points(f, x1, x2)
    fig, ax = plt.subplots(subplot_kw={"projection": "3d", "computed_zorder": False})
    fig.set_size_inches(18.5, 10.5)
    # mycmap = mpl.cm.jet
    mycmap = colorblind_safe_cmap.mpl_colormap.reversed()
    ax.plot_surface(
        X1,
        X2,
        Z,
        cmap=mycmap,
        antialiased=True,
        linewidth=0.2,
        edgecolor="k",
        rcount=len(X1),
        ccount=len(X1[0]),
        alpha=1,
        zorder=3,
    )
    zax_min, zax_max = ax.get_zlim()
    zax_min, zax_max = compute_zax_min_max(zax_min, zax_max, zfactor, is_inverse)
    ax.set_zlim(zax_min, zax_max)

    if is_remove_extra_zlables:
        ticks = ax.get_zticks()
        labels = ax.get_zticklabels()
        if is_inverse:
            is_prv = False
            _zmax = Z.max()
            for tick_val, label in zip(ticks, labels):
                if is_prv:
                    label.set_visible(False)
                if tick_val > _zmax:
                    is_prv = True
        else:
            _zmin = 1.1 * Z.min()
            for tick_val, label in zip(ticks, labels):
                if tick_val < _zmin:
                    label.set_visible(False)

    ax.contourf(
        X1,
        X2,
        Z,
        zdir="z",
        offset=zax_min,
        cmap=mycmap,
        extend="both",
        levels=50,
        alpha=0.4,
        zorder=2,
    )
    ax.contour(
        X1,
        X2,
        Z,
        zdir="z",
        offset=zax_min,
        cmap=mycmap,
        # colors='k',
        extend="both",
        levels=50,
        alpha=1,
        zorder=2,
        linewidths=0.5,
        # linestyles='--',
    )
    if len(X_data) > 0:
        y_data = [f(x) for x in X_data]
        if is_scatter_objective_space:
            ax.scatter(
                X_data[:, 0],
                X_data[:, 1],
                y_data,
                c="magenta",
                marker="+",
                s=100,
                alpha=1,
                zorder=4,
            )
        if is_scatter_search_space:
            ax.scatter(
                X_data[:, 0],
                X_data[:, 1],
                zax_min,
                c="red",
                marker="+",
                s=100,
                alpha=1,
                zorder=4,
            )
        if (
            is_scatter_search_space
            and is_scatter_search_space
            and is_connect_search_obj
        ):
            for i, x in enumerate(X_data):
                ax.plot(
                    [x[0], x[0]],  # X stays constant
                    [x[1], x[1]],  # Y stays constant
                    [zax_min, y_data[i]],  # Z goes from z1 to z2
                    color="k",
                    linestyle="--",
                    linewidth=1,
                    zorder=2,
                )
    if is_colorbar:
        zmin, zmax = Z.min(), Z.max()
        sm = plt.cm.ScalarMappable(cmap=mycmap, norm=plt.Normalize(zmin, zmax))
        fig.colorbar(
            sm,
            ax=ax,
            shrink=0.7,
            ticks=np.linspace(zmin, zmax, 5),
            orientation="vertical",
            extend="both",
        )
    if is_axis_names:
        ax.set_xlabel(r"$x_1$", labelpad=10)
        ax.set_ylabel(r"$x_2$", labelpad=10)
        zlabel = r"$f\!\br{\bm{x}}$"
        if is_inverse:
            zlabel = r"$\text{\textbf{\textcolor{red}{(inversed)}}}$ " + zlabel
        ax.set_zlabel(zlabel, labelpad=zlabelpad)
    if is_white_facecolor:
        ax.get_xaxis().set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.get_yaxis().set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.get_zaxis().set_pane_color((1.0, 1.0, 1.0, 0.0))
    return fig, ax
