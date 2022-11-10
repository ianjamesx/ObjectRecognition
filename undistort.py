import imageio
import argparse
import numpy as np
from scipy.ndimage import map_coordinates


def get_rotation_matrix(rad, ax):
    ax = np.array(ax)
    assert len(ax.shape) == 1 and ax.shape[0] == 3
    ax = ax / np.sqrt((ax**2).sum())
    R = np.diag([np.cos(rad)] * 3)
    R = R + np.outer(ax, ax) * (1.0 - np.cos(rad))

    ax = ax * np.sin(rad)
    R = R + np.array([[0, -ax[2], ax[1]],
                      [ax[2], 0, -ax[0]],
                      [-ax[1], ax[0], 0]])

    return R


def prepare_arguments():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--i', required=True,
                        help='Paths to input image.')
    parser.add_argument('--o', required=True,
                        help='Paths to output image.')
    parser.add_argument('--i_fov', type=float, default=180,
                        help='Fisheye image field of view in degree.')
    parser.add_argument('--o_u', type=float, default=0,
                        help='Horizontal viewing angle in degree. (Right+ / Left-)')
    parser.add_argument('--o_v', type=float, default=0,
                        help='Vertical viewing angle in degree. (Down+ / Up-)')
    parser.add_argument('--o_fov', type=float, required=True,
                        help='Output image field of view in degree.')
    parser.add_argument('--o_sz', type=int, default=512,
                        help='Output image size.')
    args = parser.parse_args()
    assert 0 < args.i_fov
    assert 0 < args.o_fov and args.o_fov < 180

    # Convert degree to radian
    args.i_fov = args.i_fov * np.pi / 180
    args.o_fov = args.o_fov * np.pi / 180
    args.o_u = args.o_u * np.pi / 180
    args.o_v = args.o_v * np.pi / 180

    return args


def grid_in_3d_to_project(o_fov, o_sz, o_u, o_v):
    z = 1
    L = np.tan(o_fov / 2) / z
    x = np.linspace(L, -L, num=o_sz, dtype=np.float64)
    y = np.linspace(-L, L, num=o_sz, dtype=np.float64)
    x_grid, y_grid = np.meshgrid(x, y)
    z_grid = np.ones_like(x_grid)

    Rx = get_rotation_matrix(o_v, [1, 0, 0])
    Ry = get_rotation_matrix(o_u, [0, 1, 0])
    xyz_grid = np.stack([x_grid, y_grid, z_grid], -1).dot(Rx).dot(Ry)

    return [xyz_grid[..., i] for i in range(3)]


if __name__ == '__main__':
    # Parse arguments
    args = prepare_arguments()

    # Read fisheye image
    fisheye = np.array(imageio.imread(args.i))
    ih, iw = fisheye.shape[:2]

    # Math for rewarping
    x_grid, y_grid, z_grid = grid_in_3d_to_project(args.o_fov, args.o_sz, args.o_u, args.o_v)
    theta = np.arctan2(y_grid, x_grid)
    c_grid = np.sqrt(x_grid**2 + y_grid**2)
    rho = np.arctan2(c_grid, z_grid)
    r = rho * min(ih, iw) / args.i_fov
    coor_x = r * np.cos(theta) + iw / 2
    coor_y = r * np.sin(theta) + ih / 2

    # Rewarping to get planar
    out = np.stack([
        map_coordinates(fisheye[..., ich], [coor_y, coor_x], order=1)
        for ich in range(fisheye.shape[-1])
    ], axis=-1)
    imageio.imwrite(args.o, out)