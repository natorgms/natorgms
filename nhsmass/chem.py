#    Copyright 2022 Volikov Alexander <ab.volikov@gmail.com>
#
#    This file is part of nhsmass. 
#
#    nhsmass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nhsmass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nhsmass.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .spectrum import Spectrum
from .draw import vk

class Reaction(object):
    """
    Class for discover reaction by MS-difference methods
    """
    def __init__(self, 
        sourse: Optional["Spectrum"] = None, 
        product: Optional["Spectrum"] = None,
        ) -> None:
        """
        Init Reaction

        Parameters
        ---------
        sourse: Spectrum object
            mass spectrum of source
        product: Spectrum object
            mass spectrum of product
        """
        self.sourse = sourse
        self.product = product

    def find_modification(self, brutto_table: pd.DataFrame) -> "Reaction":
        """
        Find in source peaks that have modifed by diff-mass-es in brutto table
        Also cath them in product

        Parameters
        ----------
        brutto_table:pd.DataFrame
            table with element and their masses.
            Can be generated by function brutto_generator.brutto_gen().
        """

        self.sourse = self.sourse.drop_unassigned().calc_mass()
        self.product = self.product.drop_unassigned().calc_mass()

        sourse_mass = self.sourse.table['calc_mass'].values
        product_mass = self.product.table['calc_mass'].values

        sourse_mass_num = len(sourse_mass)
        product_mass_num = len(product_mass)

        mdiff = np.zeros((sourse_mass_num, product_mass_num), dtype=float)
        for x in range(sourse_mass_num):
            for y in range(product_mass_num):
                mdiff[x,y] = product_mass[y]-sourse_mass[x]

        sourse_index = np.array([])
        product_index = np.array([])
        for i, row in brutto_table.iterrows():
            arr = np.where(mdiff == row['mass'])
            sourse_index = np.hstack([sourse_index, arr[0]])
            product_index = np.hstack([product_index, arr[1]])

        self.sourse.table['modified'] = False
        self.product.table['modified'] = False

        self.sourse.table.loc[sourse_index,'modified'] = True
        self.product.table.loc[product_index,'modified'] = True

        return Reaction(sourse=self.sourse, product=self.product)

    def draw_modification(self,
        ax: Optional[plt.axes] = None,
        sourse: bool = True,
        product: bool = True,
        sourse_color: str = 'red',
        product_color: str = 'blue',
        size: float = 5
        )->None:
        """
        Plot Van-Krevelen for modifed peaks in product and sourse

        Parameters
        ----------
        ax: plt.axes
            Optional. Use external ax
        sourse: bool
            Optional. Default True. plot sourse peaks
        product: bool
            Optional. Default True. plot product peaks
        sourse_color: str
            Optional. Default red. Color of sourse peaks
        product_color: str
            Optional. Default blue. Color of product peaks
        size: float
            Optional. Default 5. Size of dot on VK
        """

        if 'modified' not in self.product.table or 'modified' not in self.sourse.table:
            raise Exception(f"Modification hasn't calculated")

        if ax is None:
            fig, ax = plt.subplots(figsize=(4,4), dpi = 75)

        if sourse:
            self.sourse.table = self.sourse.table.loc[self.sourse.table['modified'] == True].reset_index(drop=True)
            vk(self.sourse, ax=ax, size=size, color=sourse_color, label='sourse')

        if product:
            self.product.table = self.product.table.loc[self.product.table['modified'] == True].reset_index(drop=True)
            vk(self.product, ax=ax, size=size, color=product_color, label='product')

        ax.legend()


if __name__ == '__main__':
    pass