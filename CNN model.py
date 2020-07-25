
class cnn_model():

    def __init__(self, ):
        pass
        

    def embeddings(fl1=32, fl2=32, fl3=64, dl=16, optimizer= 'RMSprop', kl = 5, layer =1 ):
        sequence_input = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
        embedded_sequences = embedding_layer(sequence_input)
        if (layer == 1):
            x = Conv1D(filters = fl1, kernel_size = kl, activation='relu')(embedded_sequences)
            x = MaxPooling1D(pool_size = kl)(x)
        elif (layer == 2):
            x = Conv1D(filters = fl1, kernel_size = kl, activation='relu')(embedded_sequences)
            x = MaxPooling1D(pool_size = kl)(x)
            x = Conv1D(filters = fl2, kernel_size = kl, activation='relu')(x)
            x = MaxPooling1D(pool_size = kl)(x)
            
        else:
            x = Conv1D(filters = fl1, kernel_size = kl, activation='relu')(embedded_sequences)
            x = MaxPooling1D(pool_size = kl)(x)
            x = Conv1D(filters = fl2, kernel_size = kl, activation='relu')(x)
            x = MaxPooling1D(pool_size = kl)(x)
            x = Conv1D(filters = fl3, kernel_size = kl, activation='relu')(x)
        x = GlobalMaxPooling1D()(x)
        x = Dense(units = dl, activation='relu')(x)
        preds = Dense(1, activation='tanh')(x)
        model = Model(sequence_input, preds)
        model.compile(loss= 'binary_crossentropy',optimizer= optimizer,
                  metrics=['acc'])
       
        return model