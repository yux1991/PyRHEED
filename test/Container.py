import A
import B
import dependency_injector.containers as containers
import dependency_injector.providers as providers

class ContainerA(containers.DeclarativeContainer):
    buttonA_press = providers.Singleton(A.A.buttonA_press)
    A = providers.Singleton(A.A)

class ContainerB(containers.DeclarativeContainer):
    buttonB_press = providers.Singleton(B.B.buttonB_press)
    B = providers.Singleton(B.B)
