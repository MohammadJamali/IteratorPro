import random
import string
from operator import itemgetter
from threading import Lock, Event


class IteratorPro:
    """
    Class implementing a wrapper for iterators

    IteratorPro tails multiple `iter()` objects and iterate them inline,  a reserved
    separated  queue  called  `extra`  is  exist  to  serve some important items and
    `iter()` out of order. Using `loop()` it loops over all collection over and over
    again. Using `blocking`, consumer have to wait until the next item is ready, but
    if  it's  left to be False,  the `default` value is being returned once there is
    nothing in the collection and a read request has arrived. IteratorPro never stop
    and raise `StopIteration` unless `def shutdown()` is being called.
    """

    def __init__(self, data=None, solid_data=False, length=None, extra=None,
                 solid_extra=False, tag=None, default=None, blocking=False,
                 timeout=1000, loop=False):
        self._default = default
        self._loop = loop
        self.tag = tag
        self._length = length
        self._timeout = timeout

        self._shutdown = False
        self._data_pack = None
        self._iterator_len = None
        self._iterator = -1
        self._write_lock = Lock()
        self._read_lock = Lock()

        if blocking:
            self._has_thing_event = Event()
            self._has_thing_event.clear()
        else:
            self._has_thing_event = None

        self._data_list = []
        if data is not None:
            self.insert(data, solid_object=solid_data)

        self._extra = []
        if extra is not None:
            self.insert_extra(extra, solid_object=solid_extra)

    def __iter__(self):
        consuming_extra = False

        # No matter whether it has data to yield or not, if it's not in shutdown state we will
        # loop over and over and wait for `def insert(self, data, location=0)` to add some data
        while True:
            with self._read_lock:
                try:
                    # extra data always have priority over normal data, if any extra data exist,
                    # it's  supposed to consume first,  because extra always consume first,  it
                    # will deleted right after consumption
                    if self._extra:
                        if not consuming_extra and self._data_pack:
                            # to continue the last step after consuming extra data
                            self._iterator = max(-1, self._iterator - 1)

                        self._data_pack = self._extra[0]
                        del self._extra[0]

                        consuming_extra = True
                    # if last selected data-pack consumed to the end it would be replace by None
                    # it means the rest of the code expecting a new data-pack to consume
                    elif not self._data_pack:
                        if self._iterator + 1 >= len(self._data_list):
                            raise StopIteration
                        self._iterator = self._iterator + 1

                        consuming_extra = False

                        self._data_pack = self._data_list[self._iterator]
                except StopIteration:
                    # iff we are allowed to loop over the collection, the selector would reset
                    # to its default value (-1), -1 means start from beginning
                    if self._loop:
                        self._iterator = -1
                        continue
                    # iff blocking mod is enabled, it waits for new data
                    elif self._has_thing_event:
                        try:
                            self._has_thing_event.clear()
                            self._has_thing_event.wait(self._timeout)
                        except Exception as ex:
                            continue
                    # if shutdown mode is enabled and it has nothing to consume, stop
                    elif self._shutdown:
                        return
                    else:
                        # return default mode
                        self._data_pack = None, self._default, self._default, None, None

                # iterable items would added like normal `list.extend` method virtually if
                # `solid_object` not set.  so here it's gonna convert an iterable to something
                # like this:
                #   id = ...insert(range(3))
                #       iterate = (id, 0)
                #       iterate = (id, 1)
                #       iterate = (id, 2)
                #
                #   id2 = ...insert(range(6), solid_object=True)
                #       iterate = (id2, range(6))
                #
                # so `insert(range(3))` has same effect as `iter([].extend(list(range(3)))`

                id, data, data_iter, solid_object, read_remove = self._data_pack
                if not solid_object and hasattr(data, '__iter__'):
                    try:
                        data = next(data_iter)
                        yield id, data
                    except StopIteration:
                        if not consuming_extra:
                            if read_remove:
                                self.delete(id)
                                self._update_iterator_len()
                            else:
                                iter_data = iter(data) \
                                    if not solid_object and hasattr(data, '__iter__') \
                                    else data
                                fresh_data = (id, data, iter_data, solid_object, read_remove)
                                self._data_list[self._iterator] = fresh_data
                        self._data_pack = None
                else:
                    yield id, data
                    self._data_pack = None

                    if read_remove:
                        self.delete(id)
                        self._update_iterator_len()

    # some times computing iterator's len is somehow time consuming, due to this fact
    # it's better to tell us whether we should update and compute the len or not
    def _update_iterator_len(self):
        if self._length:
            return

        acquired_write_lock = False
        while not self._write_lock.locked():
            try:
                self._write_lock.acquire(blocking=True, timeout=1000)
                acquired_write_lock = True
            except TimeoutError:
                pass  # to avoid deadlock, wait 1s and pool again
                # TODO: count failed tries and raise exception on too many retry

        try:
            self._iterator_len = 0

            for data in self._data_list:
                id, data, itera_data, solid_object, read_remove = data

                if data is not None or solid_object:
                    self._iterator_len += 1
                elif hasattr(data, '__len__'):
                    self._iterator_len += len(data)
                # should i include `count()` ?
        finally:
            try:
                # release the lock only if it was acquired by `_update_iterator_len`
                if acquired_write_lock:
                    self._write_lock.release()
            except Exception as ex:
                pass  # to avoid deadlock

    def __len__(self):
        return self._length + len(self._extra) if self._length \
            else (self._iterator_len if self._iterator_len else 0) + len(self._extra)

    def shutdown(self):
        with self._write_lock:
            self._shutdown = True

    def has_extra(self):
        return len(self._extra) > 0

    def loop(self, status=True):
        with self._write_lock:
            self._loop = status
        return self

    def insert_extra(self, extra, id=None, solid_object=False, allow_none=False):
        return self._insert(self._extra, extra, id, solid_object=solid_object, allow_none=allow_none)

    def insert(self, data, id=None, location=None, allow_none=False,
               solid_object=False, read_remove=False):
        id = self._insert(self._data_list, data, id, location,
                          allow_none, solid_object, read_remove)
        self._update_iterator_len()
        return id

    def _insert(self, list, data, id=None, location=None, allow_none=False,
                solid_object=False, read_remove=False):
        try:
            if not allow_none and (data is None or (hasattr(data, '__len__') and len(data) == 0)):
                return None
        except TypeError:  # TypeError: object of type 'CommandCursor' has no len()
            pass

        if not location:
            location = len(list)
        assert location >= 0, f'IteratorPro: Location expected to be more than' \
                              f' zero but got {location}'

        with self._write_lock:
            if self._shutdown:
                raise Exception('Sorry but iterator is being shutdown.'
                                ' Please restart to append new data.')

            id = id or ''.join(random.choice(string.ascii_lowercase) for i in range(4))
            iter_data = iter(data) \
                if not solid_object and hasattr(data, '__iter__') \
                else data
            list.insert(location, (id, data, iter_data, solid_object, read_remove))
            if self._has_thing_event:
                self._has_thing_event.set()
            return id

    def delete(self, id):
        with self._write_lock:
            index = list(map(itemgetter(0), self._data_list)).index(id)
            if index >= 0:
                del self._data_list[index]
            if index == self._iterator:
                self._data_pack = None
            if index <= self._iterator:
                self._iterator = max(-1, self._iterator - 1)

        return self

    def is_clean(self):
        with self._write_lock:
            return not self._data_list
