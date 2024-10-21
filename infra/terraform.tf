provider "azurerm" {
  features {}
  tenant_id       = var.tenant_id
  subscription_id = var.subscription_id
}

resource "azurerm_resource_group" "hvalfangst" {
  location = var.location
  name     = var.resource_group_name
}

resource "azurerm_service_plan" "hvalfangst" {
  name = var.azurerm_service_plan_name
  location = azurerm_resource_group.hvalfangst.location
  resource_group_name = azurerm_resource_group.hvalfangst.name
  os_type = "Linux"
  sku_name = "B1"
}

resource "azurerm_linux_web_app" "hvalfangst" {
  name = var.azurerm_linux_web_app_name
  location = azurerm_resource_group.hvalfangst.location
  resource_group_name = azurerm_resource_group.hvalfangst.name
  service_plan_id = azurerm_service_plan.hvalfangst.id
  site_config {
    always_on = false
    application_stack{
      python_version = "3.10"
    }

    # Mandatory startup command to run the API with Gunicorn on port 8000
    app_command_line = "gunicorn -k uvicorn.workers.UvicornWorker main:app"
  }

  app_settings = {
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"  # Enable SCM deployment build with virtual environment creation
  }
}
