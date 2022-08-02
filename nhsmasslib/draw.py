#    Copyright 2022 Volikov Alexander <ab.volikov@gmail.com>
#
#    This file is part of nhsmasslib. 
#
#    nhsmasslib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nhsmasslib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nhsmasslib.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt
from .mass import MassSpectrum

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns

def spectrum(spec: 'MassSpectrum',
    xlim: Tuple[Optional[float], Optional[float]] = (None, None),
    ylim: Tuple[Optional[float], Optional[float]] = (None, None),
    color: Optional[str] = 'black',
    ax: Optional[plt.axes] = None,
    **kwargs
    ) -> None:
    """
    Draw mass spectrum

    All parameters except spec is optional

    Parameters
    ----------
    spec: MassSpectrum object
        spec for plot
    xlim: Tuple (float, float)
        restrict for mass
    ylim: Tuple (float, float)
        restrict for intensity
    color: str
        color of draw
    ax: matplotlyp axes object
        send here ax to plot in your own condition
    **kwargs: dict
        additinal parameters to plot method
    """

    df = spec.copy().table

    mass = df['mass'].values
    if xlim[0] is None:
        xlim = (mass.min(), xlim[1])
    if xlim[1] is None:
        xlim = (xlim[0], mass.max())

    intensity = df['intensity'].values
    # filter first intensity and only after mass (because we will lose the information)
    intensity = intensity[(xlim[0] <= mass) & (mass <= xlim[1])]
    mass = mass[(xlim[0] <= mass) & (mass <= xlim[1])]

    # bas solution, probably it's needed to rewrite this piece
    M = np.zeros((len(mass), 3))
    M[:, 0] = mass
    M[:, 1] = mass
    M[:, 2] = mass
    M = M.reshape(-1)

    I = np.zeros((len(intensity), 3))
    I[:, 1] = intensity
    I = I.reshape(-1)

    if ax is None:
        fig, ax = plt.subplots(figsize=(4,4), dpi=75)

    ax.plot(M, I, color=color, linewidth=0.2, **kwargs)
    ax.plot([xlim[0], xlim[1]], [0, 0], color=color, linewidth=0.2, **kwargs)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel('m/z, Da')
    ax.set_ylabel('Intensity')
    ax.set_title(f'{len(spec.table)} peaks')

    return

def scatter(spec: 'MassSpectrum',
            x: str, 
            y: str,
            xlim: Tuple[Optional[float], Optional[float]] = (None, None),
            ylim: Tuple[Optional[float], Optional[float]] = (None, None),
            volume: Optional[str] = 'intensity',
            color: Optional[str] = None, 
            alpha: Optional[float] = 0.3, 
            size: Optional[float] = None,
            size_power: Optional[float] = None,
            ax: Optional[plt.axes] = None,
            **kwargs: Optional[dict]) -> None:
    """
    Draw scatter of different columns in mass-spectrum

    Parameters
    ----------
    spec: MassSpectrum object
        spec for plot
    x: str
        Name for x ordiante - columns in spec table
    y: str
        Name for y ordinate - columns in spec table
    xlim: Tuple (float, float)
        restrict for mass
    ylim: Tuple (float, float)
        restrict for intensity
    volume: str
        Name for z ordinate - columns in spec table.
        If size is none. size of dots will calculate by median of it parameter
    ax: plt.axes
        Optional, external ax
    color: str
        Optional. default None. Color for scatter.
        if None - separate color: CHO as blue, CHON as orange, CHOS as green and CHONS
    alpha: float
        Optional, default 0.3. Alpha for scatter
    size: float
        Optional. default None - normalize by intensivity to median.
    size_power: float
        Optinal. default None - plot linear dependes for volume.
        raises volume values to a power. For increae size put values > 1, for decrease <1
    **kwargs: dict
        additional parameters to scatter method
    """

    spec = spec.copy().drop_unassigned()

    if volume == 'None':
        if size is None:
            raise Exception("when wolume is 'None' there must be size value")
        s = size
    else:
        s = spec.table[volume]/spec.table[volume].median()
        if size_power is not None:
            s = np.power(s, size_power)
        if size is not None:
            s = s * size

    if color is None:
        spec.table['color'] = 'blue'
        if 'N' in spec.table:
            spec.table.loc[(spec.table['C'] > 0) & (spec.table['H'] > 0) &(spec.table['O'] > 0) & (spec.table['N'] > 0), 'color'] = 'orange'
        if 'S' in spec.table:
            spec.table.loc[(spec.table['C'] > 0) & (spec.table['H'] > 0) &(spec.table['O'] > 0) & (spec.table['N'] < 1) & (spec.table['S'] > 0), 'color'] = 'green'
            spec.table.loc[(spec.table['C'] > 0) & (spec.table['H'] > 0) &(spec.table['O'] > 0) & (spec.table['N'] > 0) & (spec.table['S'] > 0), 'color'] = 'red'
        c = spec.table['color']
    else:
        c = color

    if ax is None:
        fig, ax = plt.subplots(figsize=(4,4), dpi=75)

    ax.scatter(x=spec.table[x], y=spec.table[y], c=c, alpha=alpha, s=s, **kwargs)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel(x)
    ax.set_ylabel(y)

    return

def scatter_density(spec: 'MassSpectrum',
                    x: str, 
                    y: str,
                    xlim: Tuple[Optional[float], Optional[float]] = (None, None),
                    ylim: Tuple[Optional[float], Optional[float]] = (None, None),
                    volume: Optional[str] = 'intensity',
                    color: Optional[str] = None, 
                    alpha: Optional[float] = 0.3, 
                    size: Optional[float] = None,
                    size_power: Optional[float] = None,
                    axes: Optional[plt.axes] = None,
                    **kwargs) -> None:
    """
    Plot VK scatter with density
    Same as joinplot in seaborn
    but you can use external axes

    Parameters
    ----------
    spec: MassSpectrum object
        spec for plot
    axes: list of plt.ax
        Optional, default None. List of three axes: ax for scatter, and ax_x, ax_y for density plot
    x: str
        Name for x ordiante - columns in spec table
    y: str
        Name for y ordinate - columns in spec table
    xlim: Tuple (float, float)
        restrict for mass
    ylim: Tuple (float, float)
        restrict for intensity
    volume: str
        Name for z ordinate - columns in spec table.
        If size is none. size of dots will calculate by median of it parameter
    color: str
        Optional. default None. Color for scatter.
        if None - separate color: CHO as blue, CHON as orange, CHOS as green and CHONS
    alpha: float
        Optional, default 0.3. Alpha for scatter
    size: float
        Optional. default None - normalize by intensivity to median.
    size_power: float
        Optinal. default None - plot linear dependes for volume.
        raises volume values to a power. For increae size put values > 1, for decrease <1
    **kwargs: dict
        additional parameters to scatter method
    """

    if axes is None:
        fig = plt.figure(figsize=(6,6), dpi=100)
        gs = GridSpec(4, 4)

        ax = fig.add_subplot(gs[1:4, 0:3])
        ax_x = fig.add_subplot(gs[0,0:3])
        ax_y = fig.add_subplot(gs[1:4, 3])
    else:
        ax, ax_x, ax_y = axes

    scatter(spec, x=x, y=y, xlim=xlim, ylim=ylim, volume=volume, color=color, alpha=alpha, size=size, size_power=size_power, ax=ax, **kwargs)
    
    density(spec, col=x, color=color, ax=ax_x)
    ax_x.set_axis_off()
    ax_x.set_xlim(xlim)
    
    density(spec, col=y, color=color, ax=ax_y, vertical=True)
    ax_y.set_axis_off()
    ax_y.set_xlim(ylim)

    return

def density(spec: 'MassSpectrum',
            col: str, 
            color: Optional[str] = 'blue', 
            ax: Optional[plt.axes] = None, 
            **kwargs: Optional[dict]) -> None:
    """
    Draw KDE density for values

    Parameters
    ----------
    spec: MassSpectrum object
        spec for plot
    x: str
        Column name for draw density
    color: str
        Optional, default blue. Color of density plot
    ax: plt.axes
        Optional. External axes.
    """

    spec = spec.copy().drop_unassigned()
    total_int = spec.table['intensity'].sum()

    x = np.linspace(spec.table[col].min(), spec.table[col].max(), 100)        
    oc = np.array([])
    
    for i, el in enumerate(x[1:]):
        s = spec.table.loc[(spec.table[col] > x[i-1]) & (spec.table[col] <= el), 'intensity'].sum()
        coun = len(spec.table) * s/total_int
        m = (x[i-1] + x[i])/2
        oc = np.append(oc, [m]*int(coun))

    if ax is None:
        fig, ax = plt.subplots(figsize=(4,4), dpi=75)
    
    sns.kdeplot(x = oc, ax=ax, color=color, fill=True, alpha=0.1, bw_adjust=2, **kwargs)
    ax.set_xlabel(col)

    return

def density_2D(spec: 'MassSpectrum', 
                x: str, 
                y: str, 
                cmap: Optional[str] ="YlGnBu", 
                ax: Optional[plt.axes] = None, 
                shade: Optional[bool] = True
                ) -> None:
    """
    Draw Van-Krevelen density

    All parameters is optional

    Parameters
    ----------
    spec: MassSpectrum object
        spec for plot
    x: str
        Name for x ordiante - columns in spec table
    y: str
        Name for y ordinate - columns in spec table
    cmap: str
        color map
    ax: matplotlib ax
        external ax
    shade: bool
        show shade
    """
    sns.kdeplot(spec.table[x], spec.table[y], ax=ax, cmap=cmap, shade=shade)

    return

def vk(spec: "MassSpectrum",
       *args: Optional[list],
       **kwargs: Optional[dict]) -> None:
    """
    Scatter Van-Krevelin diagramm (O/C vs H/C)

    Parameters
    ----------
    spec: MassSpectrum object
        Mass-spectrum
    *args: list
        arguments to send scatter function
    *kwargs: dict
        arguments to send scatter function    
    """
    if 'O/C' or 'H/C' not in spec.table:
        spec = spec.copy().calculate_hc_oc()

    scatter(spec=spec, x='O/C', y='H/C', xlim=(0, 1), ylim=(0, 2.2), *args, **kwargs)

    return

if __name__ == '__main__':
    pass