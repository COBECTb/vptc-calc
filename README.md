# vptc-calc
Калькулятор ВПТС

docker build -t vptc-calculator .

docker run --rm -it \
  -v "$(pwd)/calc-vpts.py":/app/calc-vpts.py:ro \
  -v "$(pwd)/output":/app/output \
  vptc-calculator
