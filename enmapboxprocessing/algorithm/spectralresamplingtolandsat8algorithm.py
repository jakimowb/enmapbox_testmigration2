from enmapboxprocessing.algorithm.spectralresamplingbyresponsefunctionconvolutionalgorithmbase import \
    SpectralResamplingByResponseFunctionConvolutionAlgorithmBase
from typeguard import typechecked


@typechecked
class SpectralResamplingToLandsat8Algorithm(SpectralResamplingByResponseFunctionConvolutionAlgorithmBase):
    A_CODE = True

    def displayName(self) -> str:
        return 'Spectral resampling (to Landsat 8 OLI)'

    def shortDescription(self) -> str:
        link = self.htmlLink(
            'https://www.usgs.gov/core-science-systems/nli/landsat/landsat-satellite-missions',
            'Landsat')
        return super().shortDescription() + f'\nFor more information see the {link} missions website.'

    def code(self):
        from collections import OrderedDict

        responses = OrderedDict()
        # responses['Coastal aerosol'] = [(429, 0.002), (430, 0.003), (431, 0.008), (432, 0.025), (433, 0.086), (434, 0.254), (435, 0.518), (436, 0.765), (437, 0.909), (438, 0.958), (439, 0.977), (440, 0.984), (441, 0.989), (442, 0.987), (443, 0.994), (444, 0.993), (445, 1.0), (446, 0.997), (447, 0.983), (448, 0.973), (449, 0.906), (450, 0.746), (451, 0.471), (452, 0.226), (453, 0.093), (454, 0.037), (455, 0.015), (456, 0.006), (457, 0.002)]
        responses['Blue'] = [(443, 0.001), (444, 0.002), (445, 0.004), (446, 0.007), (447, 0.013), (448, 0.027), (449, 0.059), (450, 0.131), (451, 0.271), (452, 0.494), (453, 0.724), (454, 0.858), (455, 0.894), (456, 0.903), (457, 0.911), (458, 0.91), (459, 0.899), (460, 0.898), (461, 0.89), (462, 0.884), (463, 0.877), (464, 0.881), (465, 0.875), (466, 0.88), (467, 0.887), (468, 0.892), (469, 0.888), (470, 0.861), (471, 0.849), (472, 0.841), (473, 0.828), (474, 0.844), (475, 0.866), (476, 0.868), (477, 0.89), (478, 0.913), (479, 0.91), (480, 0.919), (481, 0.932), (482, 0.932), (483, 0.954), (484, 0.956), (485, 0.962), (486, 0.956), (487, 0.953), (488, 0.979), (489, 0.989), (490, 0.986), (491, 0.989), (492, 0.982), (493, 0.969), (494, 0.967), (495, 0.977), (496, 0.989), (497, 0.981), (498, 0.967), (499, 0.955), (500, 0.964), (501, 0.966), (502, 0.967), (503, 0.982), (504, 0.982), (505, 0.966), (506, 0.963), (507, 0.972), (508, 0.996), (509, 1.0), (510, 0.956), (511, 0.845), (512, 0.535), (513, 0.191), (514, 0.048), (515, 0.014), (516, 0.005), (517, 0.003), (518, 0.002), (519, 0.001)]
        responses['Green'] = [(519, 0.001), (520, 0.002), (521, 0.003), (522, 0.003), (523, 0.005), (524, 0.007), (525, 0.01), (526, 0.016), (527, 0.026), (528, 0.041), (529, 0.071), (530, 0.123), (531, 0.212), (532, 0.354), (533, 0.546), (534, 0.741), (535, 0.865), (536, 0.927), (537, 0.955), (538, 0.954), (539, 0.959), (540, 0.961), (541, 0.965), (542, 0.97), (543, 0.952), (544, 0.961), (545, 0.978), (546, 0.978), (547, 0.977), (548, 0.981), (549, 0.991), (550, 1.0), (551, 0.992), (552, 0.983), (553, 0.984), (554, 0.978), (555, 0.965), (556, 0.957), (557, 0.946), (558, 0.948), (559, 0.959), (560, 0.967), (561, 0.978), (562, 0.966), (563, 0.953), (564, 0.958), (565, 0.97), (566, 0.979), (567, 0.983), (568, 0.981), (569, 0.975), (570, 0.967), (571, 0.979), (572, 0.978), (573, 0.976), (574, 0.974), (575, 0.98), (576, 0.969), (577, 0.969), (578, 0.968), (579, 0.983), (580, 0.98), (581, 0.964), (582, 0.969), (583, 0.984), (584, 0.987), (585, 0.974), (586, 0.946), (587, 0.904), (588, 0.809), (589, 0.685), (590, 0.525), (591, 0.345), (592, 0.19), (593, 0.088), (594, 0.035), (595, 0.014), (596, 0.006), (597, 0.003), (598, 0.001)]
        responses['Red'] = [(628, 0.002), (629, 0.004), (630, 0.007), (631, 0.015), (632, 0.03), (633, 0.067), (634, 0.149), (635, 0.3), (636, 0.527), (637, 0.764), (638, 0.905), (639, 0.948), (640, 0.951), (641, 0.947), (642, 0.952), (643, 0.963), (644, 0.975), (645, 0.984), (646, 0.984), (647, 0.983), (648, 0.983), (649, 0.974), (650, 0.959), (651, 0.956), (652, 0.956), (653, 0.953), (654, 0.957), (655, 0.982), (656, 1.0), (657, 0.992), (658, 0.985), (659, 0.982), (660, 0.977), (661, 0.973), (662, 0.981), (663, 0.997), (664, 0.992), (665, 0.981), (666, 0.964), (667, 0.962), (668, 0.971), (669, 0.967), (670, 0.967), (671, 0.95), (672, 0.849), (673, 0.609), (674, 0.316), (675, 0.124), (676, 0.046), (677, 0.018), (678, 0.007), (679, 0.003), (680, 0.001)]
        responses['NIR'] = [(838, 0.001), (839, 0.002), (840, 0.003), (841, 0.005), (842, 0.007), (843, 0.011), (844, 0.017), (845, 0.028), (846, 0.048), (847, 0.084), (848, 0.145), (849, 0.25), (850, 0.404), (851, 0.583), (852, 0.745), (853, 0.89), (854, 0.96), (855, 0.987), (856, 0.973), (857, 0.981), (858, 0.996), (859, 1.0), (860, 0.99), (861, 0.981), (862, 0.976), (863, 0.972), (864, 0.957), (865, 0.951), (866, 0.947), (867, 0.953), (868, 0.951), (869, 0.948), (870, 0.94), (871, 0.951), (872, 0.956), (873, 0.966), (874, 0.97), (875, 0.937), (876, 0.891), (877, 0.789), (878, 0.635), (879, 0.448), (880, 0.289), (881, 0.175), (882, 0.1), (883, 0.058), (884, 0.035), (885, 0.021), (886, 0.012), (887, 0.008), (888, 0.005), (889, 0.003), (890, 0.002), (891, 0.001)]
        responses['SWIR-1'] = [(1524, 0.001), (1525, 0.001), (1526, 0.002), (1527, 0.002), (1528, 0.002), (1529, 0.002), (1530, 0.003), (1531, 0.003), (1532, 0.004), (1533, 0.004), (1534, 0.005), (1535, 0.006), (1536, 0.006), (1537, 0.007), (1538, 0.008), (1539, 0.01), (1540, 0.011), (1541, 0.012), (1542, 0.014), (1543, 0.016), (1544, 0.019), (1545, 0.022), (1546, 0.026), (1547, 0.03), (1548, 0.035), (1549, 0.04), (1550, 0.048), (1551, 0.055), (1552, 0.066), (1553, 0.076), (1554, 0.089), (1555, 0.102), (1556, 0.12), (1557, 0.139), (1558, 0.163), (1559, 0.188), (1560, 0.22), (1561, 0.253), (1562, 0.291), (1563, 0.33), (1564, 0.376), (1565, 0.421), (1566, 0.474), (1567, 0.526), (1568, 0.579), (1569, 0.632), (1570, 0.677), (1571, 0.721), (1572, 0.755), (1573, 0.788), (1574, 0.821), (1575, 0.854), (1576, 0.873), (1577, 0.892), (1578, 0.9), (1579, 0.907), (1580, 0.913), (1581, 0.919), (1582, 0.923), (1583, 0.927), (1584, 0.927), (1585, 0.926), (1586, 0.925), (1587, 0.924), (1588, 0.924), (1589, 0.924), (1590, 0.923), (1591, 0.921), (1592, 0.922), (1593, 0.923), (1594, 0.925), (1595, 0.927), (1596, 0.935), (1597, 0.943), (1598, 0.944), (1599, 0.946), (1600, 0.946), (1601, 0.946), (1602, 0.947), (1603, 0.948), (1604, 0.95), (1605, 0.953), (1606, 0.951), (1607, 0.95), (1608, 0.953), (1609, 0.956), (1610, 0.959), (1611, 0.962), (1612, 0.96), (1613, 0.958), (1614, 0.96), (1615, 0.961), (1616, 0.961), (1617, 0.96), (1618, 0.961), (1619, 0.961), (1620, 0.965), (1621, 0.968), (1622, 0.969), (1623, 0.971), (1624, 0.974), (1625, 0.977), (1626, 0.979), (1627, 0.981), (1628, 0.981), (1629, 0.981), (1630, 0.989), (1631, 0.996), (1632, 0.998), (1633, 1.0), (1634, 1.0), (1635, 1.0), (1636, 0.997), (1637, 0.993), (1638, 0.986), (1639, 0.979), (1640, 0.967), (1641, 0.955), (1642, 0.936), (1643, 0.917), (1644, 0.879), (1645, 0.841), (1646, 0.797), (1647, 0.752), (1648, 0.694), (1649, 0.637), (1650, 0.573), (1651, 0.51), (1652, 0.452), (1653, 0.394), (1654, 0.343), (1655, 0.292), (1656, 0.251), (1657, 0.211), (1658, 0.181), (1659, 0.151), (1660, 0.128), (1661, 0.107), (1662, 0.091), (1663, 0.075), (1664, 0.064), (1665, 0.053), (1666, 0.045), (1667, 0.037), (1668, 0.032), (1669, 0.026), (1670, 0.023), (1671, 0.019), (1672, 0.016), (1673, 0.013), (1674, 0.011), (1675, 0.01), (1676, 0.008), (1677, 0.007), (1678, 0.006), (1679, 0.005), (1680, 0.004), (1681, 0.004), (1682, 0.003), (1683, 0.003), (1684, 0.002), (1685, 0.002), (1686, 0.002), (1687, 0.001), (1688, 0.001)]
        responses['SWIR-2'] = [(2051, 0.001), (2052, 0.001), (2053, 0.001), (2054, 0.002), (2055, 0.002), (2056, 0.002), (2057, 0.002), (2058, 0.002), (2059, 0.003), (2060, 0.003), (2061, 0.003), (2062, 0.004), (2063, 0.004), (2064, 0.005), (2065, 0.005), (2066, 0.006), (2067, 0.006), (2068, 0.007), (2069, 0.008), (2070, 0.009), (2071, 0.01), (2072, 0.011), (2073, 0.012), (2074, 0.014), (2075, 0.015), (2076, 0.017), (2077, 0.019), (2078, 0.021), (2079, 0.023), (2080, 0.026), (2081, 0.029), (2082, 0.032), (2083, 0.035), (2084, 0.04), (2085, 0.045), (2086, 0.051), (2087, 0.056), (2088, 0.063), (2089, 0.07), (2090, 0.079), (2091, 0.089), (2092, 0.101), (2093, 0.113), (2094, 0.128), (2095, 0.145), (2096, 0.162), (2097, 0.18), (2098, 0.203), (2099, 0.227), (2100, 0.254), (2101, 0.281), (2102, 0.311), (2103, 0.343), (2104, 0.377), (2105, 0.413), (2106, 0.45), (2107, 0.489), (2108, 0.522), (2109, 0.555), (2110, 0.593), (2111, 0.634), (2112, 0.663), (2113, 0.69), (2114, 0.722), (2115, 0.757), (2116, 0.776), (2117, 0.793), (2118, 0.814), (2119, 0.836), (2120, 0.846), (2121, 0.854), (2122, 0.868), (2123, 0.884), (2124, 0.886), (2125, 0.886), (2126, 0.895), (2127, 0.907), (2128, 0.91), (2129, 0.911), (2130, 0.918), (2131, 0.926), (2132, 0.93), (2133, 0.932), (2134, 0.937), (2135, 0.941), (2136, 0.943), (2137, 0.943), (2138, 0.943), (2139, 0.943), (2140, 0.945), (2141, 0.948), (2142, 0.949), (2143, 0.95), (2144, 0.95), (2145, 0.949), (2146, 0.953), (2147, 0.957), (2148, 0.953), (2149, 0.947), (2150, 0.949), (2151, 0.953), (2152, 0.951), (2153, 0.947), (2154, 0.947), (2155, 0.947), (2156, 0.952), (2157, 0.958), (2158, 0.953), (2159, 0.946), (2160, 0.948), (2161, 0.951), (2162, 0.952), (2163, 0.952), (2164, 0.949), (2165, 0.945), (2166, 0.943), (2167, 0.94), (2168, 0.943), (2169, 0.948), (2170, 0.945), (2171, 0.94), (2172, 0.939), (2173, 0.938), (2174, 0.942), (2175, 0.947), (2176, 0.947), (2177, 0.944), (2178, 0.947), (2179, 0.952), (2180, 0.949), (2181, 0.945), (2182, 0.94), (2183, 0.934), (2184, 0.935), (2185, 0.939), (2186, 0.939), (2187, 0.939), (2188, 0.935), (2189, 0.929), (2190, 0.927), (2191, 0.926), (2192, 0.931), (2193, 0.937), (2194, 0.934), (2195, 0.928), (2196, 0.931), (2197, 0.936), (2198, 0.936), (2199, 0.934), (2200, 0.935), (2201, 0.938), (2202, 0.946), (2203, 0.957), (2204, 0.956), (2205, 0.952), (2206, 0.957), (2207, 0.963), (2208, 0.964), (2209, 0.964), (2210, 0.964), (2211, 0.962), (2212, 0.963), (2213, 0.964), (2214, 0.962), (2215, 0.961), (2216, 0.959), (2217, 0.958), (2218, 0.958), (2219, 0.958), (2220, 0.953), (2221, 0.947), (2222, 0.952), (2223, 0.959), (2224, 0.96), (2225, 0.96), (2226, 0.955), (2227, 0.948), (2228, 0.952), (2229, 0.959), (2230, 0.961), (2231, 0.961), (2232, 0.956), (2233, 0.949), (2234, 0.953), (2235, 0.96), (2236, 0.964), (2237, 0.967), (2238, 0.964), (2239, 0.96), (2240, 0.965), (2241, 0.973), (2242, 0.978), (2243, 0.981), (2244, 0.983), (2245, 0.984), (2246, 0.985), (2247, 0.985), (2248, 0.991), (2249, 1.0), (2250, 0.998), (2251, 0.993), (2252, 0.992), (2253, 0.993), (2254, 0.996), (2255, 1.0), (2256, 0.999), (2257, 0.997), (2258, 0.994), (2259, 0.991), (2260, 0.988), (2261, 0.984), (2262, 0.986), (2263, 0.989), (2264, 0.985), (2265, 0.978), (2266, 0.975), (2267, 0.973), (2268, 0.974), (2269, 0.977), (2270, 0.976), (2271, 0.975), (2272, 0.974), (2273, 0.974), (2274, 0.968), (2275, 0.96), (2276, 0.957), (2277, 0.955), (2278, 0.955), (2279, 0.956), (2280, 0.947), (2281, 0.937), (2282, 0.922), (2283, 0.907), (2284, 0.895), (2285, 0.884), (2286, 0.855), (2287, 0.824), (2288, 0.785), (2289, 0.744), (2290, 0.699), (2291, 0.652), (2292, 0.603), (2293, 0.553), (2294, 0.503), (2295, 0.453), (2296, 0.404), (2297, 0.356), (2298, 0.316), (2299, 0.278), (2300, 0.245), (2301, 0.212), (2302, 0.186), (2303, 0.162), (2304, 0.141), (2305, 0.122), (2306, 0.107), (2307, 0.092), (2308, 0.08), (2309, 0.069), (2310, 0.061), (2311, 0.053), (2312, 0.046), (2313, 0.04), (2314, 0.036), (2315, 0.031), (2316, 0.028), (2317, 0.024), (2318, 0.021), (2319, 0.019), (2320, 0.017), (2321, 0.015), (2322, 0.013), (2323, 0.011), (2324, 0.01), (2325, 0.009), (2326, 0.008), (2327, 0.007), (2328, 0.006), (2329, 0.006), (2330, 0.005), (2331, 0.004), (2332, 0.004), (2333, 0.003), (2334, 0.003), (2335, 0.003), (2336, 0.002), (2337, 0.002), (2338, 0.002), (2339, 0.002), (2340, 0.001), (2341, 0.001)]
        # responses['Pan'] = [(490, 0.001), (491, 0.002), (492, 0.003), (493, 0.004), (494, 0.006), (495, 0.009), (496, 0.016), (497, 0.023), (498, 0.043), (499, 0.067), (500, 0.124), (501, 0.196), (502, 0.323), (503, 0.472), (504, 0.598), (505, 0.715), (506, 0.776), (507, 0.817), (508, 0.832), (509, 0.838), (510, 0.849), (511, 0.862), (512, 0.863), (513, 0.86), (514, 0.859), (515, 0.858), (516, 0.857), (517, 0.856), (518, 0.858), (519, 0.863), (520, 0.861), (521, 0.856), (522, 0.853), (523, 0.85), (524, 0.853), (525, 0.857), (526, 0.859), (527, 0.86), (528, 0.862), (529, 0.863), (530, 0.86), (531, 0.855), (532, 0.864), (533, 0.879), (534, 0.886), (535, 0.889), (536, 0.895), (537, 0.902), (538, 0.906), (539, 0.909), (540, 0.912), (541, 0.914), (542, 0.91), (543, 0.903), (544, 0.909), (545, 0.92), (546, 0.922), (547, 0.919), (548, 0.913), (549, 0.905), (550, 0.893), (551, 0.879), (552, 0.877), (553, 0.879), (554, 0.878), (555, 0.876), (556, 0.873), (557, 0.869), (558, 0.875), (559, 0.885), (560, 0.89), (561, 0.893), (562, 0.886), (563, 0.874), (564, 0.876), (565, 0.882), (566, 0.891), (567, 0.901), (568, 0.904), (569, 0.903), (570, 0.908), (571, 0.914), (572, 0.915), (573, 0.913), (574, 0.916), (575, 0.92), (576, 0.921), (577, 0.921), (578, 0.924), (579, 0.929), (580, 0.93), (581, 0.93), (582, 0.938), (583, 0.949), (584, 0.947), (585, 0.94), (586, 0.941), (587, 0.944), (588, 0.946), (589, 0.947), (590, 0.942), (591, 0.936), (592, 0.94), (593, 0.947), (594, 0.942), (595, 0.934), (596, 0.934), (597, 0.938), (598, 0.941), (599, 0.944), (600, 0.952), (601, 0.964), (602, 0.967), (603, 0.968), (604, 0.968), (605, 0.968), (606, 0.965), (607, 0.961), (608, 0.957), (609, 0.953), (610, 0.949), (611, 0.946), (612, 0.948), (613, 0.952), (614, 0.955), (615, 0.956), (616, 0.959), (617, 0.963), (618, 0.964), (619, 0.964), (620, 0.966), (621, 0.969), (622, 0.973), (623, 0.977), (624, 0.978), (625, 0.978), (626, 0.974), (627, 0.969), (628, 0.97), (629, 0.972), (630, 0.973), (631, 0.973), (632, 0.97), (633, 0.966), (634, 0.966), (635, 0.967), (636, 0.967), (637, 0.966), (638, 0.972), (639, 0.981), (640, 0.981), (641, 0.978), (642, 0.974), (643, 0.971), (644, 0.963), (645, 0.953), (646, 0.953), (647, 0.958), (648, 0.964), (649, 0.971), (650, 0.969), (651, 0.965), (652, 0.967), (653, 0.971), (654, 0.974), (655, 0.977), (656, 0.983), (657, 0.99), (658, 0.988), (659, 0.984), (660, 0.988), (661, 0.996), (662, 0.999), (663, 1.0), (664, 1.0), (665, 0.999), (666, 0.998), (667, 0.997), (668, 0.993), (669, 0.987), (670, 0.986), (671, 0.986), (672, 0.956), (673, 0.914), (674, 0.78), (675, 0.61), (676, 0.439), (677, 0.267), (678, 0.167), (679, 0.094), (680, 0.058), (681, 0.035), (682, 0.023), (683, 0.015), (684, 0.011), (685, 0.008), (686, 0.006), (687, 0.004), (688, 0.003), (689, 0.002), (690, 0.002)]
        return responses