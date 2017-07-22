from copyTask import get_sample
from datetime import datetime
import numpy as np
import keras

LOG_PATH_BASE="/proj/ciptmp/te58rone/logs/"     #this is for tensorboard callbacks




def test_model(model, sequence_length=None):
    input_dim = model.input_dim
    output_dim = model.output_dim
    batch_size = model.batch_size

    I, V, sw = next(get_sample(batch_size=batch_size, in_bits=input_dim, out_bits=output_dim,
                                        max_size=sequence_length, min_size=sequence_length))
    Y = np.asarray(model.predict(I, batch_size=batch_size))

    if not np.isnan(Y.sum()): #checks for a NaN anywhere
        Y = (Y > 0.5).astype('float64')
        #print(Y)
        acc = (V[:, -sequence_length:, :] == Y[:, -sequence_length:, :]).mean() * 100
    else:
        ntm = model.layers[0]
        k, b, M = ntm.get_weights()
        import pudb; pu.db
        acc = 0
    return acc


def train_model(model, epochs=10, min_size=5, max_size=20, callbacks=None):
    input_dim = model.input_dim
    output_dim = model.output_dim
    batch_size = model.batch_size

    import pudb; pu.db
    sample_generator = get_sample(batch_size=batch_size, in_bits=input_dim, out_bits=output_dim,
                                                max_size=max_size, min_size=min_size)
    model.fit_generator(sample_generator, 1, epochs=epochs, callbacks=callbacks)

    #for i in range(epochs): 
    #    I, V, sw = get_sample(batch_size=batch_size, in_bits=input_dim, out_bits=output_dim,
    #                                    max_size=max_size, min_size=min_size)
    #    model.fit(I, V, sample_weight=sw, callbacks=callbacks, epochs=i+1, batch_size=batch_size, initial_epoch=i)
    print("done training")


def lengthy_test(model, testrange=[5,10,20,40,80], epochs=100):
    ts =datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    log_path = LOG_PATH_BASE + ts + "_-_" + model.name 
    tb = keras.callbacks.TensorBoard(log_dir=log_path, write_graph=True)
    callbacks = [tb, keras.callbacks.TerminateOnNaN()]

    for i in testrange:
        acc = test_model(model, sequence_length=i)
        print("the accuracy for length {0} was: {1}%".format(i,acc))

    train_model(model, epochs=epochs, callbacks=callbacks)

    for i in testrange:
        import pudb; pu.db
        acc = test_model(model, sequence_length=i)
        print("the accuracy for length {0} was: {1}%".format(i,acc))
    return