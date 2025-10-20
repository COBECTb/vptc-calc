# vptc-calc
Калькулятор ВПТК

```
docker build -t vptc-calculator .
```

```
docker run --rm -it \
  -v "$(pwd)/calc-vpts.py":/app/calc-vpts.py:ro \
  -v "$(pwd)/output":/app/output \
  vptc-calculator
```

![alt text](images/vptc_roller_12_8_34_90.png "vptc_roller_12_8_34_90")
