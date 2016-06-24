DATA_DIR=$SNAP_DATA
if [ ! -d "$DATA_DIR/files" ]; then
    echo "Configuring snapstore-example..."
    cp -r $SNAP/files $DATA_DIR
fi
    
FILES=$DATA_DIR/files store.py
    
