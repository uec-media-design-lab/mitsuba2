#include <random>
#include <enoki/stl.h>
#include <mitsuba/core/ray.h>
#include <mitsuba/core/properties.h>
#include <mitsuba/render/bsdf.h>
#include <mitsuba/render/emitter.h>
#include <mitsuba/render/integrator.h>
#include <mitsuba/render/records.h>

NAMESPACE_BEGIN(mitsuba)

/** \brief Invert integrator (:monosp:`invert`)
 *  Forward rendering : Path tracer
 *  Backward rendering : Invert tracer (propagate spectrum from sensor to scene through ray)
 *  -----------------------------------------
 * 
 *  This integrator is mainly used to propagate spectrum information for scene objects.
 *  In forward rendering, this integrator supports simple path tracing. 
 *  In backward rendering, this integrator transports spectrum on film to scene. 
 * */

template <typename Float, typename Spectrum>
class InvertIntegrator : public MonteCarloIntegrator<Float, Spectrum> {
public:
    MTS_IMPORT_BASE(MonteCarloIntegrator, m_max_depth, m_rr_depth);
    MTS_IMPORT_TYPES(Scene, Sampler, Medium, Emitter, EmitterPtr, BSDF, BSDFPtr);

    InvertIntegrator(const Properties &props) : Base(props) { }

    std::pair<Spectrum, Mask> sample(const Scene *scene,
                                     Sampler *sampler,
                                     const RayDifferential3f &ray_,
                                     const Medium * /* medium */, 
                                     Float * /* aovs */,
                                     Mask active) const override {
        MTS_MASKED_FUNCTION(ProfilerPhase::SamplingIntegratorSample, active);

        RayDifferential3f ray = ray_;

        // Tracks radiance scaling due to index of refraction changes 
        Float eta(1.f);

        // MIS weight for intesected emitters (set by prev. iteration)
        Float emission_weight(1.f);

        Spectrum throughput(1.f), result(0.f);

        // ---------------------- First intersection ----------------------

        SurfaceInteraction3f si = scene->ray_intersect(ray, active);
        Mask valid_ray = si.is_valid();
        EmitterPtr emitter = si.emitter(scene);

    }
};

NAMESPACE_END(mitsuba)