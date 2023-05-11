# Install CUDA in WSL

## CUDA in Windows
Install CUDA in windows using the [official installer](https://developer.nvidia.com/cuda-downloads).
This step is crucial, as we will forward the CUDA libraries from windows to WSL and not install
them sepetately in WSL. 

## CUDA in WSL
To install CUDA in WSL, we will need to install the CUDA toolkit.
Source [here](https://collabnix.com/introducing-new-docker-cli-api-support-for-nvidia-gpus-under-docker-engine-19-03-0-beta-release/)

### 1. create a file named `nvidia-container-runtime-script.sh` with the following content:
```bash
curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
```

### 2. run the script:
```bash
sudo bash nvidia-container-runtime-script.sh
```

### 3. install the CUDA toolkit:
```bash
apt-get install nvidia-container-runtime
```

#### 3.1 check if the installation was successful:
```bash
which nvidia-container-runtime-hook
```

```bash
nvidia-smi
```

### 4. restart docker:
```bash
sudo service docker restart
```

### 5. Test if CUDA is working:
```bash
docker run -it --rm --gpus all ubuntu nvidia-smi
```

