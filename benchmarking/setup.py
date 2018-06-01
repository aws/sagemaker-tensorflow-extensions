from setuptools import setup

setup(name="sagemaker_tensorflow_pipemode_benchmarking",
      version="1.0.0",
      packages=["pipemode_benchmark"],
      entry_points={
          'console_scripts': ["tensorflow_pipemode_benchmark = pipemode_benchmark.benchmark:main",
                              "tensorflow_pipemode_local_benchmark = pipemode_benchmark.local_benchmark:main"]
      },
      include_package_data=True,
      package_data={'pipemode_benchmark': ['docker/*']},
      install_requires=['boto3', 'tensorflow'])
