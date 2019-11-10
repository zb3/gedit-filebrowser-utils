class FileBrowserSelector:
    COLUMN_LOCATION = 3
    SCROLL_ALIGN = 0.3

    def __init__(self, window, view):
        self.window = window
        self.view = view
        self.bus = window.get_message_bus()

    def get_model(self):
        # we only want to return this when it's a file browser model
        # bookmarks model is not of our interest
        model = self.view.get_model()

        if model.__gtype__.name == 'GeditFileBrowserStore':
            return model

        return None

    def select_current_document(self):
        doc = self.window.get_active_document()
        if doc:
            gfile = doc.get_location()
            if gfile:
                self.select_uri(gfile.get_uri())

    def select_uri(self, uri):
        try:
            msg = self.bus.send_sync('/plugins/filebrowser', 'get_root')
        except TypeError:
            return

        root = msg.props.location
        root_uri = root.get_uri()

        if not uri.startswith(root_uri + '/'):
            return

        model = self.get_model()
        if model:
            self.select_uri_from_iter(model, model.get_iter_first(), uri)

    def select_uri_from_iter(self, model, itr, uri):
        while itr is not None:
            gfile = model.get_value(itr, self.COLUMN_LOCATION)

            if gfile is None:
                # the directory is not yet loaded
                # it will load asynchronously after expanding the row

                path = model.get_path(itr)

                self.set_pending_expand(model, path, uri)
                self.view.expand_to_path(path)

                break

            gfile_uri = model.get_value(itr, self.COLUMN_LOCATION).get_uri()

            if gfile_uri == uri:
                self.select_iter(model, itr)
                break

            elif uri.startswith(gfile_uri + '/'):
                itr = model.iter_children(itr)
            else:
                itr = model.iter_next(itr)


    def set_pending_expand(self, model, path, uri):
        self.pending_model = model
        self.pending_path = path
        self.pending_uri = uri
        self.end_loading_handler = model.connect('end-loading', self.end_loading_cb)

    def end_loading_cb(self, model, itr):
        if not self.pending_model or self.pending_model != model:
            return

        path = self.pending_path
        uri = self.pending_uri

        self.pending_model.disconnect(self.end_loading_handler)
        self.pending_path = None
        self.pending_model = None

        self.select_uri_from_iter(model, model.get_iter(path), uri)

    def select_parent(self):
        if not self.get_model():
            return False

        # selection mode is multiple, yet we only care about the first selected item
        sel = self.view.get_selection()
        model, rows = sel.get_selected_rows()

        if rows:
            row = rows[0]

            moved = row.up()
            # currently we don't change the root (could use backspace)

            self.select_iter(model, model.get_iter(row))

    def select_iter(self, model, itr):
        path = model.get_path(itr)
        self.view.expand_to_path(path)

        sel = self.view.get_selection()
        sel.unselect_all()
        sel.select_iter(itr)

        self.view.scroll_to_cell(path, None, True, self.SCROLL_ALIGN)
        self.view.grab_focus()

