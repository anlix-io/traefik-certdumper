ACME_PATH=$1
CERT_DIR=$2

mkdir -p $CERT_DIR
python -u  /acme_converter.py $ACME_PATH $CERT_DIR
while true
do
  inotifywait -e modify $ACME_PATH
  python -u /acme_converter.py $ACME_PATH $CERT_DIR
done

