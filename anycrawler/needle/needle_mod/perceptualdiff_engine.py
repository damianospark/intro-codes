import subprocess
import os
import datetime

from PIL import Image

from needle.engines.base import EngineBase


class Engine(EngineBase):

    perceptualdiff_path = 'perceptualdiff'
    perceptualdiff_output_png = True

    def assertSameFiles(self, output_file, baseline_file, threshold):
        # Calculate threshold value as a pixel number instead of percentage.
        width, height = Image.open(output_file).size
        threshold = int(width * height * threshold)

        # diff_ppm = output_file.replace(".png", ".diff.ppm")
        diff_ppm = output_file.replace(".png", ".diff.png")  # gnoopy 수정
        cmd = "%s -verbose -threshold %d -output %s %s %s" % (
            self.perceptualdiff_path, threshold, diff_ppm, baseline_file, output_file)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        perceptualdiff_stdout, _ = process.communicate()
        print('cmd =>', cmd)

        # Sometimes perceptualdiff returns a false positive with this exact message:
        # 'FAIL: Images are visibly different\n0 pixels are different\n\n'
        # We catch that here.

        # gnoopy 수정
        # if process.returncode == 0 or b'\n0 pixels are different' in perceptualdiff_stdout:
        #     # No differences found, but make sure to clean up the .ppm in case it was created.
        #     if os.path.exists(diff_ppm):
        #         os.remove(diff_ppm)
        #     return
        # else:
        #     if os.path.exists(diff_ppm):
        #         if self.perceptualdiff_output_png:
        #             # Convert the .ppm output to .png
        #             diff_png = diff_ppm.replace("diff.ppm", "diff.png")
        #             Image.open(diff_ppm).save(diff_png)
        #             os.remove(diff_ppm)
        #             diff_file_msg = ' (See %s)' % diff_png
        #         else:
        #             diff_file_msg = ' (See %s)' % diff_ppm
        #     else:
        #         diff_file_msg = ''
        #     raise AssertionError("The new screenshot '%s' did not match "
        #                          "the baseline '%s'%s:\n%s"
        #                          % (output_file, baseline_file, diff_file_msg, perceptualdiff_stdout))

        #
        if os.path.exists(diff_ppm):
            os.rename(diff_ppm, diff_ppm.split('.')[-3] + '-' + datetime.datetime.now().strftime('%Y%m%d') + '.diff.png')
            filename = diff_ppm.split('.')[-3] + '-' + datetime.datetime.now().strftime('%Y%m%d') + '.txt'
            # Write the string to the file
            total_pixels = 0

            with open(filename, 'w') as file:
                if isinstance(perceptualdiff_stdout, bytes):
                    perceptualdiff_stdout = perceptualdiff_stdout.decode('utf-8')
            # Find the line with 'pixels are different'
                for line in perceptualdiff_stdout.splitlines():
                    if 'pixels are different' in line:
                        # Extract the number of different pixels
                        diff_pixels = int(line.split()[0])
                        # Calculate the ratio
                        total_pixels = width * height
                        diff_ratio = (diff_pixels / total_pixels) * 100
                        print(f"Diff pixels: {diff_pixels}")
                        print(f"Diff Ratio: {diff_ratio:.1f}%")
                        file.write(f"Total Pixel is {total_pixels}\n")
                        file.write(f"Diff Pixel is {diff_pixels}\n")
                        file.write(f"Diff Ratio is {diff_ratio:.1f}%\n")
                        break
                file.write(perceptualdiff_stdout)
                print(perceptualdiff_stdout)

        return
