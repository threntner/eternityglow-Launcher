import ctypes
import platform  # Neu hinzufügen

def optimize_gpu():
    if platform.system() != "Windows":  # Nur für Windows relevant
        return
        
    try:
        import nvidia_smi
        nvidia_smi.nvmlInit()
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        nvidia_smi.nvmlDeviceSetGpuOperationMode(handle, nvidia_smi.NVML_GOM_ALL_ON)
        nvidia_smi.nvmlShutdown()
    except (ImportError, AttributeError) as e:  # Spezifischere Fehler
        print(f"GPU optimization skipped: {str(e)}")

def optimize_timer():
    if platform.system() != "Windows":
        return
        
    try:
        winmm = ctypes.WinDLL('winmm')
        winmm.timeBeginPeriod(1)
    except Exception as e:
        print(f"Timer optimization failed: {str(e)}")