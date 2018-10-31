from scipy.ndimage.interpolation import map_coordinates
from scipy.ndimage.filters import gaussian_filter
import numpy as np

import cv2
from ..artist import Artist, constant


class ElasticTransform(Artist):

    @staticmethod
    def grid_coordinates(cvs):
        shape = cvs.shape        
        
        xg, yg, zg = np.meshgrid(
            np.arange(shape[1]),
            np.arange(shape[0]),
            np.arange(shape[2])
        )

        return xg, yg, zg

    @staticmethod
    def transform(cvs, dy, dx, coords, mode):
        
        xg, yg, zg = coords

        indices = (
            np.reshape(yg+dy, (-1, 1)),
            np.reshape(xg+dx, (-1, 1)),
            np.reshape(zg, (-1, 1)),
        )

        distored_image = map_coordinates(
            cvs.img, indices, order=3, mode=mode)
        
        cvs._img = distored_image.reshape(cvs.shape)


class pull(ElasticTransform):
    x = constant(0.0)
    y = constant(0.0)
    alpha = constant(1.0)
    mode = constant("constant")
    args = ("x", "y", "sigma", "alpha", "mode")
    
    def __call__(self, cvs, t=0.0):
        # https://gist.github.com/erniejunior/601cdf56d2b424757de5
        
        x = float(cvs.transform_x(self.x(t)))
        y = float(cvs.transform_y(self.y(t)))
        alpha = cvs.transform_length(self.alpha(t), is_discrete=False)

        coords = self.grid_coordinates(cvs)
        
        theta = np.arctan2(coords[1]-y, coords[0]-x)        
        dx = alpha*np.cos(theta)
        dy = alpha*np.sin(theta)

        self.transform(cvs, dy, dx, coords, self.mode(t))


class distort(ElasticTransform):
    sigma = constant(0.1)
    alpha = constant(10.0)
    mode = constant("constant")
    seed = constant(None)

    args = ("sigma", "alpha", "mode", "seed")
    
    def __call__(self, cvs, t=0.0):
        # https://gist.github.com/erniejunior/601cdf56d2b424757de5

        sigma = cvs.transform_length(self.sigma(t))
        alpha = cvs.transform_length(self.alpha(t), is_discrete=False)
        mode = self.mode(t)

        shape = cvs.shape
        random_state = np.random.RandomState(self.seed(t))

        coords = self.grid_coordinates(cvs)

        dx = random_state.rand(*shape) * 2 - 1
        dy = random_state.rand(*shape) * 2 - 1

        dx = gaussian_filter(dx, sigma, mode=mode)
        dy = gaussian_filter(dy, sigma, mode=mode)

        self.transform(cvs, dy*alpha, dx*alpha, coords, self.mode(t))

class motion_lines(ElasticTransform):
    alpha = constant(0.15)
    theta = constant(0.0)
    mode = constant("constant")
    args = ("alpha", "mode")
  
    def __call__(self, cvs, t=0.0):
        alpha = cvs.transform_length(self.alpha(t), is_discrete=False)
        
        theta = self.theta(t)
        mode = self.mode(t)

        coords = self.grid_coordinates(cvs)

        y = cvs.inverse_transform_y(coords[1].astype(float))
        x = cvs.inverse_transform_y(coords[0].astype(float))
        
        x = np.abs(x)
        y = np.abs(y)
        
        dx = np.cos(theta)*x
        dy = np.sin(theta)*y

        print(dx.max(), dx.min())
        
        self.transform(cvs, alpha*dy, alpha*dx, coords, self.mode(t))

