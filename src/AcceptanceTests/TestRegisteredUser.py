
    def test_open_store(self):
        if not self.store_was_set:
            self.set_stores()

        # happy
        self.enter_market()
        stores = self.app.get_all_stores(self.session_id)
        self.assertTrue(stores.success, "error: get store action failed!")
        self.assertTrue("store1" in stores.result, "error: store1 not found")
        self.assertTrue("store2" in stores.result, "error: store2 not found")
        products = self.app.get_store_products(self.session_id, "store1")
        self.assertTrue(products.success, "error: get store product action failed!")
        self.assertTrue("product1_1" in products.result, "error: product1_1 not found in store1")
        self.assertTrue("product1_2" in products.result, "error: product1_2 not found in store1")

        # sad
        r = self.app.open_store(self.session_id, "store4")
        self.assertFalse(r.success, "error: a guest has succeeded with opening a store")
        stores = self.app.get_all_stores(self.session_id)
        self.assertTrue("store4" not in stores.result, "error: guest created store was found!")

        # bad
        self.app.login(self.session_id, "user1", "password1")
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        r = self.app.open_store(self.session_id, "store5")
        self.assertFalse(r.success, "error: open store action not failed!")
        self.enter_market()
        stores = self.app.get_all_stores(self.session_id)
        self.assertTrue(stores.success and "store5" not in stores.result,
                        "error: store5 is found although created after exiting the market")

