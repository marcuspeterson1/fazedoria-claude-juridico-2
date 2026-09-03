# Contratos de conectores

O núcleo não depende destes conectores. `congelado` resolve uma pasta de entrada local autorizada.
`sync` deve ser implementado sempre como leitura. `infinitum` pode espelhar tarefas e entregas somente
fora do sandbox, com idempotência e confirmação do resultado. Os stubs recusam uso para impedir que
uma demonstração toque sistemas reais por acidente.

