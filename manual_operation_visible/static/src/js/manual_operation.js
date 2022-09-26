odoo.define('manual_operation_visible.ReconciliationRenderer', function (require) {
"use strict";

    var ReconcileRender = require('account.ReconciliationRenderer');
    ReconcileRender.LineRenderer.include({

        update: function (state) {
            console.log("state>>>>>>",state)
            state.mode = 'match_rp';
            
            return this._super.apply(this,arguments);
        }
    });


});
