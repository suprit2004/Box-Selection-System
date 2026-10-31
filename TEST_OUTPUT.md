PS E:\Box Selection System> .\.venv\Scripts\python.exe manage.py test fulfillment.tests --verbosity=2


Found 76 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, fulfillment, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying fulfillment.0001_initial... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
test_cheapest_feasible_box_selected (fulfillment.tests.test_box_selector.BoxSelectorServiceTest.test_cheapest_feasible_box_selected) ... ok
test_empty_order_returns_unpackable (fulfillment.tests.test_box_selector.BoxSelectorServiceTest.test_empty_order_returns_unpackable) ... ok
test_oversized_item_produces_actionable_diagnosis (fulfillment.tests.test_box_selector.BoxSelectorServiceTest.test_oversized_item_produces_actionable_diagnosis) ... ok
test_recommend_for_order_end_to_end (fulfillment.tests.test_box_selector.BoxSelectorServiceTest.test_recommend_for_order_end_to_end) ... ok
test_tie_breaker_minimum_void_volume (fulfillment.tests.test_box_selector.BoxSelectorServiceTest.test_tie_breaker_minimum_void_volume) ... ok
test_weight_capacity_rejection (fulfillment.tests.test_box_selector.BoxSelectorServiceTest.test_weight_capacity_rejection) ... ok
test_category_01_product_model_validation (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_01_product_model_validation)
Verifies valid creation, volume calculation, and SKU uniqueness. ... ok
test_category_02_shipping_box_model_validation (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_02_shipping_box_model_validation)
Verifies box creation, volume calculation, and code uniqueness. ... ok
test_category_03_order_and_orderitem_relationships (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_03_order_and_orderitem_relationships)
Verifies FK cascades, reverse lookup, and protection from deletion. ... ok
test_category_04_total_order_weight_calculation (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_04_total_order_weight_calculation)
Verifies correct calculation of order total weight and volume. ... ok
test_category_05_product_dimensional_feasibility (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_05_product_dimensional_feasibility)
Verifies that total volume feasibility alone does NOT guarantee physical fit. ... ok
test_category_06_product_rotation (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_06_product_rotation)
Verifies that the packing engine evaluates all 6 orthogonal spatial rotations ... ok
test_category_07_multiple_products (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_07_multiple_products)
Verifies collision-free placement and boundary adherence for a heterogeneous order: ... ok
test_category_08_multiple_quantities_of_same_product (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_08_multiple_quantities_of_same_product)
Verifies that an order with quantity > 1 (e.g. 4 coffee mugs) ... ok
test_category_09_weight_capacity_exceeded (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_09_weight_capacity_exceeded)
Verifies that a box is rejected when the order weight exceeds the box's ... ok
test_category_10_no_suitable_box_available (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_10_no_suitable_box_available)
Verifies that when no warehouse box can accommodate the order, ... ok
test_category_11_empty_order (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_11_empty_order)
Verifies that an empty order input returns UNPACKABLE without crashing ... ok
test_category_12_invalid_dimensions (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_12_invalid_dimensions)
Verifies that products with 0 length, width, or height are rejected ... ok
test_category_13_zero_or_negative_values (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_13_zero_or_negative_values)
Verifies rejection of negative dimensions, zero weights, and negative box costs. ... ok
test_category_14_multiple_eligible_boxes_different_costs (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_14_multiple_eligible_boxes_different_costs)
Verifies that when multiple boxes can accommodate an order, ... ok
test_category_15_orders_containing_oversized_products (fulfillment.tests.test_comprehensive_suite.ComprehensiveBoxSelectionTestSuite.test_category_15_orders_containing_oversized_products)
Verifies handling of an oversized product whose single dimension ... ok
test_can_delete_is_true (fulfillment.tests.test_formset.FormsetDefinitionTest.test_can_delete_is_true) ... ok
test_empty_form_renders_without_error (fulfillment.tests.test_formset.FormsetDefinitionTest.test_empty_form_renders_without_error)
empty_form must be accessible — it is used as the JS cloning template. ... ok
test_extra_is_zero (fulfillment.tests.test_formset.FormsetDefinitionTest.test_extra_is_zero)
extra=0 means Django renders no blank rows server-side. ... ok
test_min_num_is_one (fulfillment.tests.test_formset.FormsetDefinitionTest.test_min_num_is_one) ... ok      
test_validate_min_is_true (fulfillment.tests.test_formset.FormsetDefinitionTest.test_validate_min_is_true) ... ok
test_box_delete_confirm_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_box_delete_confirm_renders) ... ok
test_box_edit_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_box_edit_renders) ... ok     
test_box_list_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_box_list_renders) ... ok     
test_dashboard_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_dashboard_renders) ... ok   
test_navbar_present_on_all_key_pages (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_navbar_present_on_all_key_pages) ... ok
test_order_create_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_order_create_renders) ...
 ok
test_order_list_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_order_list_renders) ... ok 
test_product_delete_confirm_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_product_delete_confirm_renders) ... ok
test_product_edit_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_product_edit_renders) ...
 ok
test_product_list_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_product_list_renders) ...
 ok
test_recommendation_optimized_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_recommendation_optimized_renders) ... ok
test_recommendation_unpackable_renders (fulfillment.tests.test_ui_smoke.FullPageSmokeTest.test_recommendation_unpackable_renders) ... ok
test_scenario_10_duplicate_products_combined (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_10_duplicate_products_combined) ... ok
test_scenario_11_zero_items_rejected (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_11_zero_items_rejected) ... ok
test_scenario_1_single_item_order (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_1_single_item_order) ... ok
test_scenario_2_five_items (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_2_five_items) ... ok
test_scenario_3_add_then_remove_one (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_3_add_then_remove_one) ... ok
test_scenario_4_only_one_valid_row_kept (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_4_only_one_valid_row_kept) ... ok
test_scenario_5_empty_order_rejected (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_5_empty_order_rejected) ... ok
test_scenario_6_empty_form_in_template (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_6_empty_form_in_template) ... ok
test_scenario_7_total_forms_controls_validation (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_7_total_forms_controls_validation) ... ok
test_scenario_8_no_phantom_blank_row_errors (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_8_no_phantom_blank_row_errors) ... ok
test_scenario_9_delete_existing_item_via_flag (fulfillment.tests.test_formset.OrderCreateViewFormsetTest.test_scenario_9_delete_existing_item_via_flag) ... ok
test_duplicate_product_in_same_order_rejected (fulfillment.tests.test_models.OrderModelTest.test_duplicate_product_in_same_order_rejected) ... ok
test_order_totals_calculation (fulfillment.tests.test_models.OrderModelTest.test_order_totals_calculation) ... ok
test_product_sorted_dimensions (fulfillment.tests.test_models.ProductModelTest.test_product_sorted_dimensions) ... ok
test_product_validation_rejects_non_positive_dimension (fulfillment.tests.test_models.ProductModelTest.test_product_validation_rejects_non_positive_dimension) ... ok
test_product_validation_rejects_zero_weight (fulfillment.tests.test_models.ProductModelTest.test_product_validation_rejects_zero_weight) ... ok
test_product_volume_calculation (fulfillment.tests.test_models.ProductModelTest.test_product_volume_calculation) ... ok
test_box_validation_rejects_negative_cost (fulfillment.tests.test_models.ShippingBoxModelTest.test_box_validation_rejects_negative_cost) ... ok
test_box_volume_calculation (fulfillment.tests.test_models.ShippingBoxModelTest.test_box_volume_calculation) ... ok
test_box_delete (fulfillment.tests.test_views.ViewsTest.test_box_delete) ... ok
test_box_delete_confirmation_page (fulfillment.tests.test_views.ViewsTest.test_box_delete_confirmation_page) ... ok
test_box_edit (fulfillment.tests.test_views.ViewsTest.test_box_edit) ... ok
test_box_list_create_get_and_post (fulfillment.tests.test_views.ViewsTest.test_box_list_create_get_and_post) ... ok
test_dashboard_view (fulfillment.tests.test_views.ViewsTest.test_dashboard_view) ... ok
test_home_page_renders_dashboard (fulfillment.tests.test_views.ViewsTest.test_home_page_renders_dashboard) ... ok
test_order_create_post_and_recommendation_redirect (fulfillment.tests.test_views.ViewsTest.test_order_create_post_and_recommendation_redirect) ... ok
test_order_list_view (fulfillment.tests.test_views.ViewsTest.test_order_list_view) ... ok
test_product_delete_confirmation_page (fulfillment.tests.test_views.ViewsTest.test_product_delete_confirmation_page) ... ok
test_product_delete_protected_by_order (fulfillment.tests.test_views.ViewsTest.test_product_delete_protected_by_order) ... ok
test_product_delete_safe (fulfillment.tests.test_views.ViewsTest.test_product_delete_safe) ... ok
test_product_edit (fulfillment.tests.test_views.ViewsTest.test_product_edit) ... ok
test_product_list_create_get_and_post (fulfillment.tests.test_views.ViewsTest.test_product_list_create_get_and_post) ... ok
test_seed_sample_data_endpoint (fulfillment.tests.test_views.ViewsTest.test_seed_sample_data_endpoint) ... ok
test_cuboids_touching_faces_do_not_overlap (fulfillment.tests.test_packing_engine.PackingEngineTest.test_cuboids_touching_faces_do_not_overlap) ... ok
test_fluorescent_tube_volume_trap_fails (fulfillment.tests.test_packing_engine.PackingEngineTest.test_fluorescent_tube_volume_trap_fails) ... ok
test_item_fits_only_with_3d_rotation (fulfillment.tests.test_packing_engine.PackingEngineTest.test_item_fits_only_with_3d_rotation) ... ok
test_multi_item_packing_success (fulfillment.tests.test_packing_engine.PackingEngineTest.test_multi_item_packing_success) ... ok
test_single_item_fits_without_rotation (fulfillment.tests.test_packing_engine.PackingEngineTest.test_single_item_fits_without_rotation) ... ok

----------------------------------------------------------------------
Ran 76 tests in 0.677s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...