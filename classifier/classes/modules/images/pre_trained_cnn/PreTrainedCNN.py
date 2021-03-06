import torch
import torch.nn as nn
from torchvision import models


class PreTrainedCNN(nn.Module):

    def __init__(self, network_params: dict, activation: bool = True):
        super().__init__()

        pre_trained_type = network_params["pretrained_model"]
        features_extraction = network_params["features_extraction"]
        self.output_size = network_params["output_size"]

        pre_trained = self.__select_pretrained_model(pre_trained_type)

        if features_extraction:
            for param in pre_trained.parameters():
                param.requires_grad = False

        self.__model = self.__add_classifier(pre_trained, pre_trained_type) if activation else pre_trained

    @staticmethod
    def __select_pretrained_model(pretrained_model: str) -> nn.Module:
        pretrained_models_map = {
            "resnet": models.resnet18,
            "alexnet": models.alexnet,
            "vgg": models.vgg11_bn,
            "squeezenet": models.squeezenet1_0,
            "densenet": models.densenet121,
            "inception": models.inception_v3
        }
        return pretrained_models_map[pretrained_model](pretrained=True)

    def __add_classifier_to_resnet(self, model: nn.Module) -> nn.Module:
        """ Initializes Resnet18 """
        model.fc = nn.Linear(model.fc.in_features, self.output_size)
        return model

    def __add_classifier_to_alexnet(self, model: nn.Module) -> nn.Module:
        """ Initializes AlexNet """
        model.classifier[6] = nn.Linear(model.classifier[6].in_features, self.output_size)
        return model

    def __add_classifier_to_vgg(self, model: nn.Module) -> nn.Module:
        """ Initializes VGG11_bn """
        model.classifier[6] = nn.Linear(model.classifier[6].in_features, self.output_size)
        return model

    def __add_classifier_to_squeezenet(self, model: nn.Module) -> nn.Module:
        """ Initializes Squeezenet """
        model.classifier[1] = nn.Conv2d(512, self.output_size, kernel_size=(1, 1), stride=(1, 1))
        model.num_classes = self.output_size
        return model

    def __add_classifier_to_densenet(self, model: nn.Module) -> nn.Module:
        """ Initializes Densenet """
        num_features = model.classifier.in_features
        model.classifier = nn.Linear(num_features, self.output_size)
        return model

    def __add_classifier_to_inception(self, model: nn.Module) -> nn.Module:
        """ Initializes Inception v3 (expects 299 x 299 eye_tracking and has auxiliary output) """

        # Handle the auxiliary net
        model.AuxLogits.fc = nn.Linear(model.AuxLogits.fc.in_features, self.output_size)

        # Handle the primary net
        model.fc = nn.Linear(model.fc.in_features, self.output_size)

        return model

    def __add_classifier(self, pretrained_model: nn.Module, pretrained_model_type: str) -> nn.Module:
        initializations_map = {
            "resnet": self.__add_classifier_to_resnet,
            "alexnet": self.__add_classifier_to_alexnet,
            "vgg": self.__add_classifier_to_vgg,
            "squeezenet": self.__add_classifier_to_squeezenet,
            "densenet": self.__add_classifier_to_densenet,
            "inception": self.__add_classifier_to_inception
        }
        return initializations_map[pretrained_model_type](pretrained_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.__model(x)
