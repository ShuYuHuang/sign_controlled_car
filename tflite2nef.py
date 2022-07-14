# 工具import
import onnx
import ktc
import os
import json

# convert to onnx
result_m = ktc.onnx_optimizer.tflite2onnx_flow('/data1/model_unquant.tflite')
# 優化ONNX格式檔案
optimized_m = ktc.onnx_optimizer.onnx2onnx_flow(result_m, eliminate_tail=True, opt_matmul=False)
# 先存檔吧
onnx.save(optimized_m, '/data1/optimized.onnx')

# 系統指令操作
# 轉.onnx出來
os.system("cd /workspace/scripts && ./compilerIpevaluator_520.sh /data1/optimized.onnx")

# 讀取
with open("/data1/compiler/ioinfo.csv") as f:
  input_name=f.readline().split(",")[2]

# 設定檔
input_param_json={
    "model_info": {
        "input_onnx_file": "/data1/optimized.onnx" ,
        "model_inputs": [{
            "model_input_name": input_name,
            "input_image_folder": "/data1/img"
        }],
        "quantize_mode": "default",
        "outlier": 0.999
    },
    "preprocess": {
        "img_preprocess_method": "kneron",
        "img_channel": "RGB",
        "radix": 8,
        "keep_aspect_ratio": True,
        "pad_mode": 1,
        "p_crop": {
            "crop_x": 0,
            "crop_y": 0,
            "crop_w": 0,
            "crop_h": 0
        }
    },
    "simulator_img_files": [{
            "model_input_name": input_name,
            "input_image": "/data1/img/13.jpg"
    }]
}
# 寫入json檔
with open("/data1/input_params.json","w") as f:
  json.dump(input_param_json,f)

# 轉.bie出來
os.system("python3 /workspace/scripts/fpAnalyserCompilerIpevaluator_520.py -t 8 -c /data1/input_params.json")

# 轉設定檔
batch_input_params_json={
    "models": [
        {
            "id": 32769,
            "version": "0001",
            "path": "/data1/fpAnalyser/optimized.quan.wqbi.bie"
        }
    ]
}

# 寫入json檔
with open("/data1/batch_input_params.json","w") as f:
  json.dump(batch_input_params_json,f)

# 轉.nef檔出來
os.system("python /workspace/scripts/batchCompile_520.py -c /data1/batch_input_params.json")

# 上傳nef到某伺服器，傳完顯示儲存位址

os.system("curl --upload-file ./batch_compile/models_520.nef https://transfer.sh/models_520.nef > url.txt")
