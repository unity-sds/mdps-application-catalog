// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import _get from "lodash/get";
import { FieldLabel, SelectField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { FormikContext } from "formik";

/**const MDPS_CUSTOM_OPTIONS = [
  { id: "ogcapplicationpackage",       type_name: "OGC Application Package",       subtype_name: null,        icon: "cubes" },
  { id: "workflow",    type_name: "Workflow",    subtype_name: null,    icon: "tasks" },
  { id: "ancillary-data",    type_name: "Ancillary data",    subtype_name: null,        icon: "table" },
  { id: "auxiliary-data",     type_name: "Auxilliary data",     subtype_name: null,    icon: "chart line" },
  { id: "shell-script",     type_name: "Shell-script",     subtype_name: null,    icon: "terminal" },
  { id: "notebook",     type_name: "Notebook",     subtype_name: null,    icon: "book" },
];**/

export class ResourceTypeField extends Component {

	static contextType = FormikContext

  groupErrors = (errors, fieldPath) => {
    const fieldErrors = _get(errors, fieldPath);
    if (fieldErrors) {
      return { content: fieldErrors };
    }
    return null;
  };

  /**
   * Generate label value
   *
   * @param {object} option - back-end option
   * @returns {string} label
   */
  _label = (option) => {
    return option.type_name + (option.subtype_name ? " / " + option.subtype_name : "");
  };

  /**
   * Convert back-end options to front-end options.
   *
   * @param {array} propsOptions - back-end options
   * @returns {array} front-end options
   */
  createOptions = (propsOptions) => {
    return propsOptions
      .map((o) => ({ ...o, label: this._label(o) }))
      .sort((o1, o2) => o1.label.localeCompare(o2.label))
      .map((o) => {
        return {
          value: o.id,
          icon: o.icon,
          text: o.label,
        };
      });
  };

  componentDidMount() {
    const { values, setFieldValue } = this.context;
    const { fieldPath } = this.props;
    // only seed once if nothing’s already selected
    if (!values[fieldPath]) {
      setFieldValue(fieldPath, "ogc-application-package");
    }
  }

  render() {
    const { fieldPath, label, labelIcon, options, ...restProps } = this.props;
    const frontEndOptions = this.createOptions(options);
    return (
    	<div style={{ display: "none" }}>
	      <SelectField
	        fieldPath={fieldPath}
	        label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
	        optimized
	        aria-label={label}
	        options={frontEndOptions}
	        selectOnBlur={false}
	        {...restProps}
	      />
      	</div>
    );
  }
}

ResourceTypeField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  labelclassname: PropTypes.string,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      icon: PropTypes.string,
      type_name: PropTypes.string,
      subtype_name: PropTypes.string,
      id: PropTypes.string,
    })
  ).isRequired,
  required: PropTypes.bool,
};

ResourceTypeField.defaultProps = {
  label: i18next.t("Resource types"),
  labelIcon: "tag",
  labelclassname: "field-label-class",
  required: false,
};

export default ResourceTypeField;

export const overriddenComponents = {
	"InvenioAppRdm.Deposit.AccordionFieldFunding.container": ()=> null,
	"InvenioAppRdm.Deposit.FundingField.container": ()=> null,
	"InvenioAppRdm.Deposit.AccordionFieldAlternateIdentifiers.container": () => null,
	"InvenioAppRdm.Deposit.IdentifiersField.container": ()=> null,
	"InvenioAppRdm.Deposit.AccordionFieldRelatedWorks.container": () => null,
	"InvenioAppRdm.Deposit.RelatedWorksField.container": ()=> null,
	"InvenioAppRdm.Deposit.AccordionFieldReferences.container": ()=> null,
	"InvenioAppRdm.Deposit.ReferencesField.container": ()=> null,
	"InvenioAppRdm.Deposit.ResourceTypeField.container": ResourceTypeField,
};