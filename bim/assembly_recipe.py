from dataclasses import dataclass
from cadquery import Assembly

@dataclass
class ComponentRecipe:
    nivel : int
    name : str
    length : float
    width: float
    height: float
    inPlane: str

# esta clase se debe usar con alias cq_r
# cadquery recipiente

class AssemblyRecipe:
    def __init__():
        components : list[ComponentRecipe] = []

    def add_wk(length : float, width: float, height : float, inPlane : str = "XY"):
        
        new_c = ComponentRecipe(
            length = length, 
            width = width, 
            height = height,
            inPlane = inPlane
            )
        
        pass
        
        
    
    
    
        
    
    
