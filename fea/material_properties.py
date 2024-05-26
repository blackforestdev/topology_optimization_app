class MaterialProperties:
    def __init__(self):
        self.youngs_modulus = None
        self.poissons_ratio = None
        self.density = None

    def set_properties(self, youngs_modulus, poissons_ratio, density):
        self.youngs_modulus = youngs_modulus
        self.poissons_ratio = poissons_ratio
        self.density = density

    def get_properties(self):
        return {
            "Young's Modulus": self.youngs_modulus,
            "Poisson's Ratio": self.poissons_ratio,
            "Density": self.density
        }

