# -*- coding: utf-8 -*-

"""
***************************************************************************
    RandomExtract.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import range

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import random

from qgis.core import (QgsApplication,
                       QgsProcessingUtils)
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import ParameterSelection
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterNumber
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector


class RandomExtract(GeoAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    METHOD = 'METHOD'
    NUMBER = 'NUMBER'

    def icon(self):
        return QgsApplication.getThemeIcon("/providerQgis.svg")

    def svgIconPath(self):
        return QgsApplication.iconPath("providerQgis.svg")

    def group(self):
        return self.tr('Vector selection tools')

    def name(self):
        return 'randomextract'

    def displayName(self):
        return self.tr('Random extract')

    def defineCharacteristics(self):
        self.methods = [self.tr('Number of selected features'),
                        self.tr('Percentage of selected features')]

        self.addParameter(ParameterVector(self.INPUT,
                                          self.tr('Input layer')))
        self.addParameter(ParameterSelection(self.METHOD,
                                             self.tr('Method'), self.methods, 0))
        self.addParameter(ParameterNumber(self.NUMBER,
                                          self.tr('Number/percentage of selected features'), 0, None, 10))

        self.addOutput(OutputVector(self.OUTPUT, self.tr('Extracted (random)')))

    def processAlgorithm(self, context, feedback):
        filename = self.getParameterValue(self.INPUT)
        layer = dataobjects.getLayerFromString(filename)
        method = self.getParameterValue(self.METHOD)

        features = QgsProcessingUtils.getFeatures(layer, context)
        featureCount = QgsProcessingUtils.featureCount(layer, context)
        value = int(self.getParameterValue(self.NUMBER))

        if method == 0:
            if value > featureCount:
                raise GeoAlgorithmExecutionException(
                    self.tr('Selected number is greater than feature count. '
                            'Choose a lower value and try again.'))
        else:
            if value > 100:
                raise GeoAlgorithmExecutionException(
                    self.tr("Percentage can't be greater than 100. Set a "
                            "different value and try again."))
            value = int(round(value / 100.0000, 4) * featureCount)

        selran = random.sample(list(range(featureCount)), value)

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(layer.fields().toList(), layer.wkbType(),
                                                                     layer.crs(), context)

        total = 100.0 / featureCount
        for i, feat in enumerate(features):
            if i in selran:
                writer.addFeature(feat)
            feedback.setProgress(int(i * total))
        del writer
