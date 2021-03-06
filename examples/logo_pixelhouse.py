import numpy as np
import pixelhouse as ph
from pixelhouse.filter import gaussian_blur

pal = ph.ColorLoversPalette()(6)

C = ph.Canvas(400, 400, bg=pal[2])
lg = ph.linear_gradient(pal[0], pal[1])

C += ph.circle(color=pal[3])
C += gaussian_blur()
C += ph.circle(color=pal[3])
for i in np.arange(-6, 6, 1.0):
    C += ph.text("pixelhouse", y=i, gradient=lg)

C.save("logo_pixelhouse.png")
C.show()
