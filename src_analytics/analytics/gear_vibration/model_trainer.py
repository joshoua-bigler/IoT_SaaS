import torch
import torch.nn as nn
import wandb
import mlflow
from torch.optim.lr_scheduler import StepLR
# local
import analytics.gear_vibration.models as models


def update_wandb_config(num_epochs: int,
                        train_loader: torch.utils.data.DataLoader,
                        val_loader: torch.utils.data.DataLoader,
                        optimizer: torch.optim.Optimizer,
                        model: nn.Module,
                        criterion: nn.CrossEntropyLoss | nn.MSELoss,
                        scheduler: StepLR = None) -> None:
  # yapf: disable
  wandb.config.update({
    'epochs': num_epochs,
    'batch_size': train_loader.batch_size,
    'train_size': len(train_loader.dataset),
    'val_size': len(val_loader.dataset),
    'learning_rate': optimizer.param_groups[0]['lr'],
    'model': str(model),
    'criterion': str(criterion),
    'optimizer': str(optimizer),
    'scheduler': f'type={scheduler.__class__.__name__}, step_size={scheduler.step_size}, gamma={scheduler.gamma}' if scheduler else 'None',
    'num_par': sum(p.numel() for p in model.parameters() if p.requires_grad),
    'optimizer': {
        'type': str(optimizer.__class__.__name__),
        'lr': optimizer.param_groups[0]['lr'],
        'momentum': optimizer.param_groups[0].get('momentum', None),
        'weight_decay': optimizer.param_groups[0].get('weight_decay', None)
    }
  }, allow_val_change=True)
  # yapf: enable


def train_model(model: nn.Module,
                criterion: nn.CrossEntropyLoss,
                optimizer: torch.optim.Optimizer,
                train_loader: torch.utils.data.DataLoader,
                val_loader: torch.utils.data.DataLoader,
                num_epochs: int,
                device: torch.device,
                scheduler: StepLR = None,
                log: bool = True,
                patience: int = 10) -> nn.Module:
  with mlflow.start_run(run_name='cnn_w64_v0.0.1') as run:
    model.to(device)
    best_val_loss = float('inf')
    counter = 0
    for epoch in range(num_epochs):
      model.train()
      running_loss = 0.0
      correct = 0
      total = 0
      for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
      train_accuracy = 100 * correct / total
      train_loss = running_loss / len(train_loader)
      if scheduler:
        scheduler.step()
      if log:
        wandb.log({
            'epoch': epoch + 1,
            'train_loss': train_loss,
            'train_accuracy': train_accuracy,
            'learning_rate': optimizer.param_groups[0]['lr']
        })
      model.eval()
      val_loss = 0.0
      val_correct = 0
      val_total = 0
      with torch.no_grad():
        for inputs, labels in val_loader:
          inputs, labels = inputs.to(device), labels.to(device)
          outputs = model(inputs)
          loss = criterion(outputs, labels)
          val_loss += loss.item()
          _, predicted = torch.max(outputs.data, 1)
          val_total += labels.size(0)
          val_correct += (predicted == labels).sum().item()
      val_accuracy = 100 * val_correct / val_total
      val_loss = val_loss / len(val_loader)
      # if log:
      #   wandb.log({'val_loss': val_loss, 'val_accuracy': val_accuracy})
      print(f'Epoch [{epoch + 1}/{num_epochs}], Training Loss: {train_loss:.4f}, Validation Loss: {val_loss:.4f}, Training Accuracy: {train_accuracy:.2f}%, Validation Accuracy: {val_accuracy:.2f}%') # yapf: disable
      if val_loss < best_val_loss:
        best_val_loss = val_loss
        counter = 0
        best_model_state = model.state_dict()
      else:
        counter += 1
        if counter >= patience:
          print(f'Early stopping at epoch {epoch + 1}')
          if best_model_state:
            model.load_state_dict(best_model_state)
          break
    mlflow.pytorch.log_model(model, 'model', input_example=inputs.to("cpu").numpy())
    mlflow.register_model(model_uri=f'runs:/{run.info.run_id}/model', name='cnn_w64')
  return model


class ModelTrainer:
  ''' Model trainer for training and validating a PyTorch model. '''

  def __init__(self,
               model: nn.Module,
               model_name: str,
               criterion: nn.Module,
               optimizer: torch.optim.Optimizer,
               train_loader: torch.utils.data.DataLoader,
               val_loader: torch.utils.data.DataLoader,
               num_epochs: int,
               device: torch.device,
               version: str,
               mlflow_expiriment: str,
               scheduler: StepLR = None,
               config: dict = None,
               patience: int = 20,
               log: bool = True,
               mlflow_url: str = 'http://localhost:5000'):
    self.model = model.to(device)
    self.model_name = model_name
    self.criterion = criterion
    self.optimizer = optimizer
    self.train_loader = train_loader
    self.val_loader = val_loader
    self.num_epochs = num_epochs
    self.device = device
    self.scheduler = scheduler
    self.config = config or {}
    self.patience = patience
    self.log = log
    self.best_val_loss = float('inf')
    self.counter = 0
    self.best_model_state = None
    self.version = version
    self._run_id = None
    mlflow.set_tracking_uri(mlflow_url)
    mlflow.set_experiment(mlflow_expiriment)

  def train(self, tags: dict = None):
    ''' Train the model. 

        Parameters
        ----------
        tags: Tags to be added to the model in MLflow.
    
    '''
    with mlflow.start_run(run_name=self.model_name) as run:
      self._run_id = run.info.run_id
      self.model.to(self.device)
      if self.log:
        self._log_config()
      for epoch in range(self.num_epochs):
        train_loss, train_acc = self._train_one_epoch(epoch)
        val_loss, val_acc = self._validate(epoch)
        print(f'Epoch [{epoch + 1}/{self.num_epochs}], Training Loss: {train_loss:.4f}, Validation Loss: {val_loss:.4f}, Training Accuracy: {train_acc:.2f}%, Validation Accuracy: {val_acc:.2f}%') # yapf: disable
        if val_loss < self.best_val_loss:
          self.best_val_loss = val_loss
          self.counter = 0
          self.best_model_state = self.model.state_dict()
        else:
          self.counter += 1
          if self.counter >= self.patience:
            print(f'Early stopping at epoch {epoch + 1}')
            if self.best_model_state:
              self.model.load_state_dict(self.best_model_state)
            break
      if self.log:
        self._log_model(run=run, tags=tags)
      return self.model

  def _log_config(self):
    optimizer_params = self.optimizer.param_groups[0]
    mlflow.log_params({
        'epochs': self.num_epochs,
        'batch_size': self.train_loader.batch_size,
        'train_size': len(self.train_loader.dataset),
        'val_size': len(self.val_loader.dataset),
        'learning_rate': optimizer_params['lr'],
        'model': self.model.__class__.__name__,
        'criterion': self.criterion.__class__.__name__,
        'num_parameters': sum(p.numel() for p in self.model.parameters() if p.requires_grad),
        'optimizer_type': self.optimizer.__class__.__name__,
        'optimizer_momentum': optimizer_params.get('momentum', 0.0),
        'optimizer_weight_decay': optimizer_params.get('weight_decay', 0.0)
    })
    mlflow.set_tags({'version': self.version})
    if self.scheduler:
      mlflow.log_params({
          'scheduler_type': self.scheduler.__class__.__name__,
          'scheduler_step_size': getattr(self.scheduler, 'step_size', None),
          'scheduler_gamma': getattr(self.scheduler, 'gamma', None)
      })
    if self.config:
      mlflow.log_params({k: v for k, v in self.config.items()})

  def _log_model(self, run: mlflow.entities.Run, tags: dict = None):
    self.model.cpu()
    sample_batch, _ = next(iter(self.train_loader))
    example_input = sample_batch[0].unsqueeze(0).numpy()
    mlflow.pytorch.log_model(self.model,
                             artifact_path='model',
                             input_example=example_input,
                             code_paths=[models.__file__])
    if tags:
      mlflow.register_model(model_uri=f'runs:/{run.info.run_id}/model', name=self.model_name, tags=tags)
    self.model.to(self.device)

  def _train_one_epoch(self, epoch):
    self.model.train()
    running_loss, correct, total = 0.0, 0, 0
    for inputs, labels in self.train_loader:
      inputs, labels = inputs.to(self.device), labels.to(self.device)
      self.optimizer.zero_grad()
      outputs = self.model(inputs)
      loss = self.criterion(outputs, labels)
      loss.backward()
      self.optimizer.step()
      running_loss += loss.item()
      _, predicted = torch.max(outputs.data, 1)
      total += labels.size(0)
      correct += (predicted == labels).sum().item()
    if self.scheduler:
      self.scheduler.step()
    train_loss = running_loss / len(self.train_loader)
    train_accuracy = 100 * correct / total
    if self.log:
      mlflow.log_metric('train_loss', train_loss, step=epoch)
      mlflow.log_metric('train_accuracy', train_accuracy, step=epoch)
    return train_loss, train_accuracy

  def _validate(self, epoch):
    self.model.eval()
    val_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
      for inputs, labels in self.val_loader:
        inputs, labels = inputs.to(self.device), labels.to(self.device)
        outputs = self.model(inputs)
        loss = self.criterion(outputs, labels)
        val_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    val_accuracy = 100 * correct / total
    val_loss /= len(self.val_loader)
    if self.log:
      mlflow.log_metric('val_loss', val_loss, step=epoch)
      mlflow.log_metric('val_accuracy', val_accuracy, step=epoch)
    return val_loss, val_accuracy

  def get_tmp_run_id(self) -> str | None:
    return self._run_id
